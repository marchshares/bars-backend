from queue import Queue
from typing import List
import logging

from functions.message import Message
from functions.message.message_consumer import MessageConsumer


class MessagePublisher():
    _consumers: List[MessageConsumer]

    def __init__(self):
        self._consumers = []

    def register(self, consumer: MessageConsumer):
        logging.info("Register consumer: %s", consumer.get_name())
        self._consumers.append(consumer)

    def publish(self, message : Message):
        for c in self._consumers:
            c.consume_message(message)