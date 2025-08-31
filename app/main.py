# main.py
import logging

from infrastructure.logging_setup import setup_logging
from presentation.handler import blastn_callback
from consumer import RabbitmqConsumer


def main() -> None:
    setup_logging()

    consumer = RabbitmqConsumer(blastn_callback)
    consumer.start()


if __name__ == "__main__":
    logging.getLogger("pika").setLevel(logging.WARNING)
    main()