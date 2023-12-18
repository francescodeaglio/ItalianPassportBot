import time
from datetime import datetime, timedelta

import pytz
from passport_website_query import PassportWebsiteQuery

from databases.user_db import UserDB
from queues.queue_producer import QueueProducer


def entry_bookable(entry, delay_minutes=0):
    now = datetime.now(tz=pytz.timezone("Europe/Rome")) + timedelta(
        minutes=delay_minutes
    )
    now_hour, now_minute = now.hour, now.minute
    bookable_hour, bookable_minutes = entry["hour"].split(".")
    bookable_hour, bookable_minutes = int(bookable_hour), int(bookable_minutes)

    if now_hour > bookable_hour:
        return True
    elif now_hour == bookable_hour:
        return now_minute > bookable_minutes
    return False


def main():
    user_db = UserDB()
    pwc = PassportWebsiteQuery()

    queue_producer = QueueProducer("new_availability")

    while True:
        provinces = user_db.get_all_active_provinces()
        # provinces = office_db.get_all_provinces()

        print(f"Polling: {provinces}")

        queue_producer.open_connection()
        for province in provinces:
            avail = pwc.get_availability_province(province)

            for entry in avail:
                if entry_bookable(entry):
                    print("ADDED ENTRY to NEW QUEUE", entry)
                    queue_producer.publish_new_message(
                        {
                            "province": province,
                            "availability": entry,
                            "operation": "INSERT",
                        }
                    )
                elif entry_bookable(entry, delay_minutes=5):
                    # the entry will be bookable in less than 5 minutes
                    print("ADDED SCHEDULED ENTRY to NEW QUEUE", entry)
                    queue_producer.publish_new_message(
                        {
                            "province": province,
                            "availability": entry,
                            "operation": "INSERT SCHEDULED",
                        }
                    )
                else:
                    print("IGNORED ENTRY", entry)

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
