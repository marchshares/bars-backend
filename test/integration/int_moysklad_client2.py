import json
import config
import logging
from datetime import datetime
from random import randint
import pandas as pd

from functions.message.message_publisher import MessagePublisher
from functions.entity import Order, Product
from functions.services.moysklad_controller import MoySkladClient


class MoySkladClientInt:
    def __init__(self):
        self.ms_client = MoySkladClient(config.MOYSKLAD_LOGIN, config.MOYSKLAD_PASSWORD)

    def create_counterparty(self):
        order = Order(order_id="123458")
        order.client_name = "Мистер Тест"
        order.client_phone = "+7 (999) 999-9999"

        res = self.ms_client.find_or_create_counterparty(order)
        print(res)

    def get_counterparty_by_phone(self):
        client_phone = "+7 (999) 999-9999"

        res = self.ms_client.get_counterparty_by_phone(client_phone)
        print(res)

    def enrich_product_prices(self):
        order = Order(order_id="123458")

        order.products_price = 12830
        order.add_product(Product("WCCN80", None, 1))
        order.add_product(Product("WCCNANS", None, 1))
        order.add_product(Product("WCCBRST", None, 1))
        order.add_product(Product("WCCNLC", None, 1))

        df_with_prices = self.ms_client.get_product_to_price_df()
        order.enrich_product_prices(df_with_prices=df_with_prices)

        print(order.products)
        print(order.products_price, sum([p.price for p in order.products]))

    def get_product_to_price_map(self):
        res = self.ms_client.get_product_to_price_df()
        df = pd.DataFrame(res)
        print(res)

    def get_order_by_order_id(self):
        res = self.ms_client.get_order_by_order_name("474720")
        print(res)

    def test_create_order(self):
        order = Order(order_id=str(randint(100000, 999999)))
        # order = Order(order_id="275121")
        order.client_name = "Мистер Тест"
        order.client_phone = "+7 (999) 999-9999"
        order.client_email = "test@test.ru"
        order.city = "Москва"
        order.delivery_address = "TUL9, ул. Макаренко, 1А"
        order.delivery_company = "Грастин"
        order.delivery_our_price = 450.0
        order.delivery_client_price = 300.0
        order.warehouse = "Imsklad"
        # order.moment = datetime.strptime("02.01.2021 20:06:15", "%d.%m.%Y  %H:%M:%S")
        order.moment = datetime.now()

        order.payment_system = 'yakassa'
        order.payment_tax = 226.45

        order.products_price = 6470
        # order.add_product(Product("WCCNMC", None, 1))
        order.add_product(Product("WCCN80", None, 1))
        order.add_product(Product("WCCNANS", None, 1))
        # order.add_product(Product("6200697", None, 1))

        df_with_prices = self.ms_client.get_product_to_price_df()
        order.enrich_product_prices(df_with_prices=df_with_prices)
        ms_order = self.ms_client.create_order(order, state='Доставлен')
        if ms_order is not None:
            self.ms_client.create_demand(ms_order_id=ms_order['id'], order=order)

    def script(self):
        order_names = [
            "149941",
            "431707",
            "292722",
            "291342",
            "401341",
            "104564",
            "131098",
            "586824",
            "860038",
            "791302",
            "474720",
            "549520",
            "693740",
            "256788",
            "608128",
            "527456",
            "632243",
        ]
        for name in order_names:
            self.ms_client.remove_order_by_order_name(name)

print(datetime.now())
MoySkladClientInt().script()
# MoySkladClientInt().enrich_product_prices()
print(datetime.now())


