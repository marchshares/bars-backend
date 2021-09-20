from enum import Enum, auto
import json
import copy
import datetime

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class MessageType(Enum):
    DUMMY = auto(),
    ORDER_STATUS_CHANGED = auto()


class Message():

    def __init__(self, tp: MessageType, body: dict, creator_name):
        self._tp = tp
        self._body = copy.deepcopy(body)
        self._creator_name = creator_name

        self._body['message_created'] = datetime.datetime.today().strftime(DATE_FORMAT)

    def get_type(self):
        return self._tp

    def get_body(self):
        return self._body

    def get_creator_name(self):
        return self._creator_name

    def __str__(self) -> str:
        return str(self._tp) + ": " + str(self._body)

