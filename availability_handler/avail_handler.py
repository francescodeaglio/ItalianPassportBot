import logging

from utils import _message_builder

from common.databases import AvailabilitiesDB
from common.databases.user_db import UserDB
from common.queues.queue_producer import QueueProducer

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)
logging.getLogger("pika").propagate = False


class AvailHandler:
    def __init__(self):
        self.avail_db_connection = AvailabilitiesDB()
        self.user_db_connection = UserDB()
        self.message_queue = QueueProducer("message")

    def handle_new_availability(self, entry: dict, scheduled=False):
        availability_dict, province = entry["availability"], entry["province"]

        if availability_dict["availabilities"] is None:
            return

        new_availabilities = self.avail_db_connection.insert_new_availability(
            availability_dict
        )

        if len(new_availabilities) > 0:
            logger.log(
                logging.INFO, f"NEW AVAILABILITIES for {province}: {new_availabilities}"
            )
            self._publish_new_availability(
                province, availability_dict, new_availabilities, scheduled
            )

    def _publish_new_availability(
        self,
        province: str,
        availability_dict: dict,
        new_availabilities: list,
        scheduled: bool = False,
    ):
        chat_ids_and_channels = (
            self.user_db_connection.get_all_chat_ids_and_channels_for_province(
                province)
        )

        if len(chat_ids_and_channels) == 0:
            return

        message_content = _message_builder(
            availability_dict, new_availabilities, scheduled
        )

        self.message_queue.open_connection()

        for chat_id, channel in chat_ids_and_channels:
            self.message_queue.publish_new_message(
                {"chat_id": chat_id, "channel": channel, "content": message_content}
            )

        self.message_queue.close_connection()

    def set_inactive(self, entry):
        province = entry["province"]
        province_availabilities = entry["availabilities"]

        query_results = self.avail_db_connection.get_active_availabilities(
            province)

        to_be_updated = []
        to_be_set_inactive = []

        for result in query_results:
            availability_id, office_id, day, hour, slots = result

            found = False
            for polling_result_office in province_availabilities:
                if office_id != polling_result_office["office_id"]:
                    continue

                for polling_result_slot in polling_result_office["availabilities"]:
                    if (
                        polling_result_slot["day"] == day
                        and polling_result_slot["hour"] == hour
                    ):
                        found = True

                        if polling_result_slot["slots"] != slots:
                            to_be_updated.append(
                                {
                                    "availability_id": availability_id,
                                    "slots": polling_result_slot["slots"],
                                }
                            )
                        break
            if not found:
                to_be_set_inactive.append(availability_id)

        if len(to_be_updated) > 0:
            logger.log(logging.INFO, "UPDATED AVAILABILITY" +
                       str(to_be_updated))
            self.avail_db_connection.update_slots(to_be_updated)

        if len(to_be_set_inactive) > 0:
            logger.log(
                logging.INFO, "SET NO LONGER AVAILABLE" +
                str(to_be_set_inactive)
            )
            self.avail_db_connection.set_no_longer_available(
                to_be_set_inactive)
