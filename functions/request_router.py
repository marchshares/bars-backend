import logging
import config
import re
from typing import List, Dict, AnyStr
from functions.message.message_publisher import MessagePublisher
from functions.services import ServiceController
from functions.services.cdek_controller import CdekController
from functions.services.moysklad_controller import MoySkladController
from functions.services.telegram_controller import TelegramController


def handler(request, context):
    logging.info("INCOMING_REQUEST: %s", request)
    return RequestRouter().route(request)


class RequestRouter():
    PATH_REGEXP = "(/[^\?]*)(\?|$)"
    map_path_to_controller: Dict[AnyStr, ServiceController]

    def __init__(self):
        self.map_path_to_controller = {
            "/cdek-notification": CdekController(),
            "/telegram": TelegramController(),
            "/moysklad": MoySkladController(),
        }

        publisher = MessagePublisher()
        for c in self.map_path_to_controller.values():
            c.set_message_publisher(publisher)
            publisher.register(c)

    def route(self, request):
        path = self.extract_path(request)
        logging.info("Found path: " + path)

        body = request['body']

        controller = self.map_path_to_controller.get(path)
        if not controller:
            return RequestRouter.build_bad_result("Can't find controller for path: " + path)

        logging.info("User controller: " + controller.get_name())
        controller.consume_request(body)

        return RequestRouter.build_ok_result()

    def extract_path(self, request):
        path = request['path']

        try:
            extracted = re.search(self.PATH_REGEXP, path).group(1)
            return extracted
        except Exception as e:
            logging.error("Can't extract path from " + path)
            raise e

    @staticmethod
    def build_ok_result():
        return {
            'statusCode': 200,
            'body': 'OK',
        }

    @staticmethod
    def build_bad_result(error_msg):
        logging.error(error_msg)

        return {
            'statusCode': 500,
            'body': error_msg
        }








