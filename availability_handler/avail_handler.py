import json

from telegram_utils import telegram_message_builder
from databases.availabilities_db import AvailabilitiesDB
from databases.user_db import UserDB
from queues.queue_producer import QueueProducer


class AvailHandler:

    def __init__(self):
        self.avail_db_connection = AvailabilitiesDB()
        self.user_db_connection = UserDB()
        self.message_queue = QueueProducer("message")

    def handle_new_availability(self, body):
        entry = json.loads(body)
        print(entry)
        availability_dict, province = entry["availability"], entry["province"]
        new_availabilities = self.avail_db_connection.insert_new_availability(availability_dict)
        print(new_availabilities)
        if len(new_availabilities) == 0:
            return

        self._publish_new_availability(province, availability_dict, new_availabilities)
        self.avail_db_connection.set_no_longer_available_entries(availability_dict)

    def _publish_new_availability(self, province: str, availability_dict: dict, new_availabilities: list):

        chat_ids = self.user_db_connection.get_all_chat_ids_for_province(province)
        message_content = telegram_message_builder(
            availability_dict,
            new_availabilities
        )

        if len(chat_ids) == 0:
            return

        self.message_queue.open_connection()

        for chat_id in chat_ids:
            self.message_queue.publish_new_message(
                {
                    "chat_id": chat_id,
                    "content": message_content
                }
            )

        self.message_queue.close_connection()