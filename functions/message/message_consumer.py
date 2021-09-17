from abc import ABC, abstractmethod
from functions.message import Message


class MessageConsumer(ABC):

    @abstractmethod
    def consume_message(self, msg: Message):
        pass

    def get_name(self):
        return self.__class__.__name__
