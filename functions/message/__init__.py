from enum import Enum, auto
import json
import copy
import datetime

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class MessageType(Enum):
    DUMMY = auto(),
    ORDER_STATUS_CHANGED = auto()


class Message():

    def __init__(self, m_type: MessageType, body: dict, creator_name):
        self.m_type = m_type
        self.body = copy.deepcopy(body)
        self._creator_name = creator_name

        self.body['message_created'] = datetime.datetime.today().strftime(DATE_FORMAT)

    def get_creator_name(self):
        return self._creator_name

    def __str__(self) -> str:
        return str(self.m_type) + ": " + str(self.body)

