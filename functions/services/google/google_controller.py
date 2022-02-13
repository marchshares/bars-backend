import logging

import config
from functions.message import Message
from functions.services import ServiceController
from functions.services.google.google_client import GoogleClient


class GoogleController(ServiceController):

    def __init__(self):
        _client = GoogleClient(config.GOOGLE_API_CREDENTIALS_PATH)

    def consume_request(self, request_body):
        dummy_msg = Message(self.get_name(), {"body": request_body})
        self.publish_message(dummy_msg)

    def consume_message(self, msg: Message):
        logging.info(msg)

