import os
import pika

class RabbitmqConsumer:
    def __init__(self, callback) -> None:
        self.__host = "rabbitmq"
        self.__port = 5672
        self.__username = os.environ.get('RABBITMQ_DEFAULT_USER')
        self.__password = os.environ.get('RABBITMQ_DEFAULT_PASS')
        self.__queue = os.environ.get('RABBITMQ_BLASTN_QUEUE_NAME')
        self.__callback = callback
        self.__channel = self.__create_channel()

    def __create_channel(self):
        connection_parameters = pika.ConnectionParameters(
            host=self.__host,
            port=self.__port,
            credentials=pika.PlainCredentials(
                username=self.__username,
                password=self.__password
            )
        )

        channel = pika.BlockingConnection(connection_parameters).channel()

        channel.queue_declare(
            queue=self.__queue,
            durable=True
        )

        channel.basic_qos(prefetch_count=1)

        channel.basic_consume(
            queue=self.__queue,
            auto_ack=False,  # Ensure we manually ack the messages
            on_message_callback=self.__callback
        )

        return channel

    def start(self):
        print(f'Listening to RabbitMQ on Port 5672')
        self.__channel.start_consuming()
