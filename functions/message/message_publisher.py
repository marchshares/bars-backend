from queue import Queue
from typing import List
import logging

from functions.message import Message
from functions.message.message_consumer import MessageConsumer


class MessagePublisher():
    _consumers: List[MessageConsumer]

    def __init__(self):
        self._consumers = []
        self._consumers_counter = 0

    def register(self, consumer: MessageConsumer):
        consumer.set_id(self.next_id())
        self._consumers.append(consumer)

        logging.info(f"Register consumer: {consumer.get_name()}")

    def publish(self, message: Message):
        logging.info(f"Publish message: {message}")

        creator_name = message.get_creator_name()
        for consumer in self._consumers:
            if not consumer.is_me(creator_name):
                try:
                    consumer.consume_message(message)
                except Exception as e:
                    logging.exception(f"{consumer.get_name()}: error during message processing")


    def next_id(self):
        self._consumers_counter += 1
        return self._consumers_counter
