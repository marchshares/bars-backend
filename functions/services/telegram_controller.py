import logging
import telebot
import config
from functions.message import Message, MessageType
from functions.services import ServiceController


class TelegramController(ServiceController):

    def __init__(self):
        self._bot = telebot.TeleBot(config.BOT_TOKEN)

    def consume_request(self, request_body):
        dummy_msg = Message(MessageType.DUMMY, request_body, creator_name=self.get_name())
        self.publish_message(dummy_msg)

    def consume_message(self, msg: Message):
        msg_type = msg.get_type()

        if msg_type == MessageType.ORDER_STATUS_CHANGED:
            resp = self._bot.send_message(
                config.BOT_CHAT_ID,
                text=MT.cdek_order_status_changed(msg.get_body())
            )

            logging.info(resp)


class MT():

    @staticmethod
    def cdek_order_status_changed(mapping):
        return "Изменение статуса заказа {order_id}\n\n" \
               "Номер Cdek: {cdek_number}\n" \
               "Статус: {order_status}\n" \
               "Дата: {order_status_date}\n" \
            .format_map(mapping)
