from enum import Enum, auto
import copy
import datetime

from functions import utils

HR_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class Message():

    def __init__(self, creator_name, body: dict):
        self._body = copy.deepcopy(body)
        self._creator_name = creator_name

        self._created = datetime.datetime.today().strftime(HR_DATE_FORMAT)

    def get_body(self):
        return self._body

    def set_creator_name(self, creator_name):
        self._creator_name = creator_name

    def get_creator_name(self):
        return self._creator_name

    def __str__(self) -> str:
        return f"({self._creator_name}): {self._body}"


@utils.auto_str
class OrderStatusMessage(Message):
    def __init__(self, creator_name,
                 order_id,
                 order_status,
                 delivery_name,
                 delivery_id,
                 delivery_status,
                 delivery_city,
                 delivery_status_date
    ):
        super().__init__(creator_name, body={})

        self.order_id = order_id
        self.order_status = order_status
        self.delivery_name = delivery_name
        self.delivery_id = delivery_id
        self.delivery_status = delivery_status
        self.delivery_city = delivery_city
        self.delivery_status_date = delivery_status_date

