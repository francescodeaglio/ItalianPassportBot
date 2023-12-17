import pika
from new_user_handler import UserHandler


def main():
    # rabbitmq connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()

    avail_handler = UserHandler()

    def process_new_user_callback(ch, method, properties, body):
        print(body)
        avail_handler.handle_new_user(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        # ch.basic_nack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue="new_user", on_message_callback=process_new_user_callback
    )

    print("Waiting for messages.")

    channel.start_consuming()


if __name__ == "__main__":
    main()
