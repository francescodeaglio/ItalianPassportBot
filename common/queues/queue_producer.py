import json

import pika
import os


class QueueProducer:
    def __init__(self, queue_name: str) -> None:

        rabbitmq_host = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
        rabbitmq_port = int(os.environ.get('RABBITMQ_PORT', 5672))
        rabbitmq_user = os.environ.get("RABBITMQ_USER", "guest")
        rabbitmq_pass = os.environ.get("RABBITMQ_PASSWORD", "guest")

        self.connection_params = pika.ConnectionParameters(host=rabbitmq_host,
                                                           port=rabbitmq_port,
                                                           credentials=pika.PlainCredentials(rabbitmq_user, rabbitmq_pass))

        # Rest of your code to interact with RabbitMQ

        self.queue_name = queue_name
        self.connection = None
        self.channel = None

    def publish_new_message(self, message):
        assert self.connection is not None
        self.channel.basic_publish(
            exchange="",
            routing_key=self.queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )

    def open_connection(self):
        assert self.connection is None
        self.connection = pika.BlockingConnection(
                self.connection_params
            )
        self.channel = self.connection.channel()

    def close_connection(self):
        assert self.connection is not None
        self.connection.close()
        self.channel = None
        self.connection = None

    def __enter__(self):
        self.open_connection()

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(exc_type, exc_val, exc_tb)
        self.close_connection()
