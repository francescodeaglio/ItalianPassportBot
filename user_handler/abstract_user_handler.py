import json
import logging

from telegram_utils import create_summary_message

from common.databases import AvailabilitiesDB
from common.databases.user_db import UserDB
from common.queues.queue_producer import QueueProducer

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)
logging.getLogger("pika").propagate = False


class AbstractUserHandler:
    def __init__(self):
        self.avail_db_connection = AvailabilitiesDB()
        self.user_db_connection = UserDB()
        self.message_queue = QueueProducer("message")
        self.channel = None

    def handle_new_user(self, body):
        self.user_db_connection.connection.commit()
        user = json.loads(body)
        logger.log(logging.INFO, f"New User {user}")
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
        assert self.channel is not None
        at_lest_one_user_province = self.user_db_connection.at_lest_one_user_province(
            province
        )

        join_time = self.user_db_connection.insert_new_user(chat_id, self.channel, province)

        if at_lest_one_user_province:
            # send active availabilities if we are polling for the selected province
            self._send_previous_messages_still_available(
                chat_id, province, join_time
            )

    def _remove_user_province(self, chat_id, province):
        assert self.channel is not None
        self.user_db_connection.remove_user_province(chat_id, self.channel, province)

    def _remove_user_all_provinces(self, chat_id):
        assert self.channel is not None
        self.user_db_connection.remove_user_all_provinces(chat_id, self.channel)

    def _send_previous_messages_still_available(self, chat_id, province, join_time):
        entries = self.avail_db_connection.get_slots_available_before(
            province, join_time
        )

        if len(entries) == 0:
            return

        message = create_summary_message(entries)

        self.message_queue.open_connection()
        self.message_queue.publish_new_message(
            {"chat_id": chat_id, "channel":self.channel, "content": message})
        self.message_queue.close_connection()
