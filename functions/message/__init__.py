from enum import Enum, auto
import json

class MessageType(Enum):
    DUMMY = auto()


class Message():

    def __init__(self, msg_type: MessageType, msg_body: dict):
        self.msg_type = msg_type
        self.msg_body = msg_body

    def __str__(self) -> str:
        return str(self.msg_type) + ": " + str(self.msg_body)

