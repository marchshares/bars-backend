import logging
import json
import datetime
from typing import Dict, AnyStr

from functions import utils
from functions.message import Message, HR_DATE_FORMAT, OrderStatusMessage
from functions.services import ServiceController

CDEK_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S+%f"


class CdekController(ServiceController):
    _delivery_status_map: Dict[AnyStr, Dict]

    def __init__(self) -> None:
        self._delivery_status_map = utils.load_data("functions/data/cdek_delivery_statuses.csv", "status_code")

    def consume_request(self, request_body: str):
        """
            Example of request_body:
            '{
                "type":"ORDER_STATUS",
                "date_time":"2021-09-18T22:00:03+0700",
                "uuid":"72753033-a8ea-43df-b7bf-5a588e94cc07",
                "attributes":{
                    "is_return":false,
                    "cdek_number":"1276425961",
                    "number":"123321",
                    "status_code":"1",
                    "status_date_time":"2021-09-18T15:00:03+0000",
                    "city_name":"Офис СДЭК"
                }
            }'
        :param request_body:
        :return:
        """

        obj = CdekOrderStatusObj(request_body)
        status_code = obj.status_code

        delivery_row = self._delivery_status_map.get(status_code)
        if delivery_row is None:
            raise Exception(f"Unknown cdek_order_status_code={status_code}")

        obj.status_text = delivery_row['status_text']
        order_status = delivery_row['order_status']

        if not self.is_important_status_code(status_code):
            logging.info(f"cdek_order_status: {obj.status_text}(code={status_code}) not important. Skip")
            return

        self.publish_message(
            self.create_order_status_message(obj, order_status)
        )

    def create_order_status_message(self, obj, order_status):
        return OrderStatusMessage(self.get_name(),
            order_id=obj.number,
            order_status=order_status,
            delivery_name="Cdek",  # TODO: replace to enum names of delivery companies
            delivery_id=obj.cdek_number,
            delivery_status=obj.status_text,
            delivery_city=obj.city_name,
            delivery_status_date=get_hr_date(obj.status_date_time)
      )

    def is_important_status_code(self, cdek_order_status_code):
        row = self._delivery_status_map.get(cdek_order_status_code)
        return row['order_status'] != ''

    def consume_message(self, msg: Message):
        logging.info(msg)


class CdekOrderStatusObj:
    status_text: AnyStr = None

    def __init__(self, request_body):
        body = json.loads(request_body)
        attrs = body['attributes']

        self.status_code = attrs['status_code']
        self.cdek_number = attrs['cdek_number']
        self.number = attrs['number']
        self.status_date_time = attrs['status_date_time']
        self.city_name = attrs['city_name']


def get_hr_date(cdek_status_date_time) -> str:
    dt = datetime.datetime.strptime(cdek_status_date_time, CDEK_DATE_FORMAT)
    return dt.strftime(HR_DATE_FORMAT)