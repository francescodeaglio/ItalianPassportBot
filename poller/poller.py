import time

from databases.offices_db import OfficeDB
from databases.user_db import UserDB
from passport_website_query import PassportWebsiteQuery
from queues.queue_producer import QueueProducer


def main():
    user_db = UserDB()
    pwc = PassportWebsiteQuery()
    office_db = OfficeDB()

    queue_producer = QueueProducer("new_availability")

    while True:
        provinces = user_db.get_all_active_provinces()
        # provinces = office_db.get_all_provinces()

        print(f"Polling: {provinces}")

        queue_producer.open_connection()
        for province in provinces:
            avail = pwc.get_availability_province(province)

            for entry in avail:
                queue_producer.publish_new_message(
                    {"province": province, "availability": entry, "operation": "INSERT"}
                )

            queue_producer.publish_new_message(
                {
                    "province": province,
                    "availabilities": avail,
                    "operation": "SET INACTIVE",
                }
            )
        queue_producer.close_connection()

        print("Sleeping")
        time.sleep(45)


if __name__ == "__main__":
    main()
