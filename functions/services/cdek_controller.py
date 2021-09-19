import logging
import json
from functions.message import Message, MessageType
from functions.services import ServiceController

IMPORTANT_STATUS_CODES = [
    "1",
    "2",
    "3",
    "12",
    "11",
    "18",
    "4",
    "5"
]
MAP_CODE_TO_STATUS = {
    "1": "Создан",
    "2": "Удален",
    "3": "Принят на склад отправителя",
    "12": "Принят на склад до востребования",
    "11": "Выдан на доставку",
    "18": "Возвращен на склад доставки",
    "4": "Вручен",
    "5": "Не вручен",

    "6": "Выдан на отправку в г. отправителе",
    "16": "Возвращен на склад отправителя",
    "7": "Сдан перевозчику в г. отправителе",
    "21": "Отправлен в г. транзит",
    "22": "Встречен в г. транзите",
    "13": "Принят на склад транзита",
    "17": "Возвращен на склад транзита",
    "19": "Выдан на отправку в г. транзите",
    "20": "Сдан перевозчику в г. транзите",
    "27": "Отправлен в г. отправитель",
    "8": "Отправлен в г. получатель",
    "28": "Встречен в г. отправителе",
    "9": "Встречен в г. получателе",
    "10": "Принят на склад доставки"
}


class CdekController(ServiceController):

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

        order_status = json.loads(request_body)

        order_attrs = order_status['attributes']
        order_status_code = order_attrs['status_code']
        order_status_text = MAP_CODE_TO_STATUS[order_status_code]

        if order_status_code not in IMPORTANT_STATUS_CODES:
            logging.info(f"order_status: {order_status_text}(code={order_status_code}) not important. Skip")
            return

        message = Message(MessageType.ORDER_STATUS_CHANGED,
            {
                "order_id": order_attrs['number'],
                "cdek_number": order_attrs['cdek_number'],
                "order_status": order_status_text
            },
            creator_name=self.get_name()
        )

        self.publish_message(message)

    def consume_message(self, msg: Message):
        logging.info(msg)

