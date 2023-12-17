import json

import pika

from avail_handler import AvailHandler


def main():
    # rabbitmq connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()

    avail_handler = AvailHandler()

    def process_new_availability_callback(ch, method, properties, body):
        entry = json.loads(body)

        operation = entry["operation"]

        print(entry)

        if operation == "INSERT":
            avail_handler.handle_new_availability(entry)
        elif operation == "SET INACTIVE":
            avail_handler.set_inactive(entry)
        else:
            print("Unknown operation")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        # ch.basic_nack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue="new_availability", on_message_callback=process_new_availability_callback
    )

    print("Waiting for messages.")

    channel.start_consuming()


if __name__ == "__main__":
    main()
