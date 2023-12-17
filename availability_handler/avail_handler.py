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

    def handle_new_availability(self, entry: dict):

        print(entry)

        availability_dict, province = entry["availability"], entry["province"]

        if availability_dict["availabilities"] is None:
            return

        new_availabilities = self.avail_db_connection.insert_new_availability(
            availability_dict
        )
        print(new_availabilities)
        if len(new_availabilities) > 0:
            self._publish_new_availability(province, availability_dict, new_availabilities)

    def _publish_new_availability(
            self, province: str, availability_dict: dict, new_availabilities: list
    ):
        chat_ids = self.user_db_connection.get_all_chat_ids_for_province(province)
        message_content = telegram_message_builder(
            availability_dict, new_availabilities
        )

        if len(chat_ids) == 0:
            return

        self.message_queue.open_connection()

        for chat_id in chat_ids:
            self.message_queue.publish_new_message(
                {"chat_id": chat_id, "content": message_content}
            )

        self.message_queue.close_connection()

    def set_inactive(self, entry):
        province = entry["province"]
        availabilities = entry["availabilities"]

        query_results = self.avail_db_connection.get_active_availabilities(province)

        to_be_updated = []
        to_be_set_inactive = []

        for result in query_results:
            availability_id, office_id, day, hour, slots = result

            found = False
            for polling_result in availabilities:
                if polling_result["office_id"] == office_id and polling_result["day"] == day and polling_result[
                    "hour"] == hour:
                    found = True

                    if polling_result["slots"] != slots:
                        to_be_updated.append(
                            {
                                "availability_id": availability_id,
                                "slots": polling_result["slots"]
                            }
                        )
                    break
            if not found:
                to_be_set_inactive.append(availability_id)

        print(query_results, to_be_set_inactive, to_be_updated)

        if len(to_be_updated) > 0:
            self.avail_db_connection.update_slots(to_be_updated)

        if len(to_be_set_inactive) > 0:
            self.avail_db_connection.set_no_longer_available(to_be_set_inactive)
