import json

import pika
from telegram_sender import TelegramSender


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()

    telegram_sender = TelegramSender()

    def send_message_callback(ch, method, properties, body):
        entry = json.loads(body)
        chat_id, message, msg_channel = (
            entry["chat_id"],
            entry["content"],
            entry["channel"],
        )

        if msg_channel == "TELEGRAM":
            success = telegram_sender.send_message(message, chat_id)
        else:
            success = False

        if not success:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue="message", on_message_callback=send_message_callback)

    print("Waiting for messages. To exit press CTRL+C")

    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
