from abc import ABC, abstractmethod
from functions.message import Message


class MessageConsumer(ABC):
    _id = None

    def get_id(self):
        return self._id

    def set_id(self, id):
        self._id = id
        pass

    def is_me(self, name):
        return self.get_name() == name

    def get_name(self):
        class_name = self.__class__.__name__
        if not self._id:
            return class_name

        return class_name + str(self._id)

    @abstractmethod
    def consume_message(self, msg: Message):
        pass
