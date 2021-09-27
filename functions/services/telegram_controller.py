import logging
import telebot
import config
from functions.message import Message, OrderStatusMessage
from functions.services import ServiceController


class TelegramController(ServiceController):

    def __init__(self):
        self._bot = telebot.TeleBot(config.BOT_TOKEN)

    def consume_request(self, request_body):
        dummy_msg = Message(creator_name=self.get_name(), body=request_body)
        self.publish_message(dummy_msg)

    def consume_message(self, msg: Message):
        if isinstance(msg, OrderStatusMessage):
            self._bot.send_message(
                config.BOT_CHAT_ID,
                text=MT.cdek_order_status_changed(msg)
            )



class MT():

    @staticmethod
    def cdek_order_status_changed(msg : OrderStatusMessage):
        return f"Заказ:  {msg.order_id}\n" +\
               f"Статус: {msg.order_status}\n" +\
               f"\n" +\
               f"Номер доставки:  {msg.delivery_id} ({msg.delivery_name})\n" +\
               f"Статус доставки: {msg.delivery_status} ({msg.delivery_city})\n" +\
               f"Дата: {msg.delivery_status_date}\n"

