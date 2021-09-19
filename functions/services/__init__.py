from abc import ABC, abstractmethod
from functions.message import Message
from functions.message.message_consumer import MessageConsumer

from functions.message.message_publisher import MessagePublisher


class ServiceController(MessageConsumer, ABC):
    _message_publisher: MessagePublisher

    def set_message_publisher(self, message_publisher: MessagePublisher):
        self._message_publisher = message_publisher

    @abstractmethod
    def consume_request(self, request_body):
        pass

    def publish_message(self, msg: Message):
        self._message_publisher.publish(msg)
