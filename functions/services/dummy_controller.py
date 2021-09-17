import logging
from functions.message import Message, MessageType
from functions.services import ServiceController


class DummyController(ServiceController):

    def consume_request(self, request_body: dict):
        dummy_msg = Message(MessageType.DUMMY, request_body)
        self.publish_message(dummy_msg)

    def consume_message(self, msg: Message):
        logging.info(msg)

