import json

from databases.availabilities_db import AvailabilitiesDB
from databases.user_db import UserDB
from queues.queue_producer import QueueProducer
from user_handler.telegram_utils import create_summary_message


class UserHandler:
    def __init__(self):
        self.avail_db_connection = AvailabilitiesDB()
        self.user_db_connection = UserDB()
        self.message_queue = QueueProducer("message")

    def handle_new_user(self, body):
        self.user_db_connection.connection.commit()
        user = json.loads(body)
        print(user)
        chat_id = user["chat_id"]
        province = user["province"]
        operation = user["operation"]

        if operation == "INSERT":
            self._handle_new_user_province(chat_id, province)
        elif operation == "REMOVE":
            self._remove_user_province(chat_id, province)
        elif operation == "REMOVE ALL":
            self._remove_user_all_provinces(chat_id)

    def _handle_new_user_province(self, chat_id, province):
        join_time = self.user_db_connection.insert_new_user(chat_id, province)
        self._send_previous_messages_still_available(chat_id, province, join_time)

    def _remove_user_province(self, chat_id, province):
        self.user_db_connection.remove_user_province(chat_id, province)

    def _remove_user_all_provinces(self, chat_id):
        self.user_db_connection.remove_user_all_provinces(chat_id)

    def _send_previous_messages_still_available(self, chat_id, province, join_time):
        entries = self.avail_db_connection.get_slots_available_before(
            province, join_time
        )

        print(entries)
        if len(entries) == 0:
            return

        message = create_summary_message(entries)

        self.message_queue.open_connection()
        self.message_queue.publish_new_message({"chat_id": chat_id, "content": message})
        self.message_queue.close_connection()
