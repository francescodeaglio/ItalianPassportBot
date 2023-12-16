import time

from databases.user_db import UserDB
from passport_website_query import PassportWebsiteQuery
from queues.queue_producer import QueueProducer


def main():
    user_db = UserDB()
    pwc = PassportWebsiteQuery()

    queue_producer = QueueProducer("new_availability")

    while True:
        provinces = user_db.get_all_active_provinces()

        print(f"Polling: {provinces}")

        at_lest_one_message_sent = False
        for province in provinces:
            avail = pwc.get_availability_province(province)

            for entry in avail:
                if not at_lest_one_message_sent:
                    at_lest_one_message_sent = True
                    queue_producer.open_connection()
                queue_producer.publish_new_message(
                    {"province": province, "availability": entry}
                )

        if at_lest_one_message_sent:
            queue_producer.close_connection()

        print("Sleeping")
        time.sleep(45)


if __name__ == "__main__":
    main()
