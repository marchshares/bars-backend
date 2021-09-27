import logging
from functions.message import Message
from functions.services import ServiceController


class DummyController(ServiceController):

    def consume_request(self, request_body):
        dummy_msg = Message(self.get_name(), {"body": request_body})
        self.publish_message(dummy_msg)

    def consume_message(self, msg: Message):
        logging.info(msg)

