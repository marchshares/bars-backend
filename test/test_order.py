import json
from datetime import datetime

import config
import logging

from unittest import TestCase, mock

from functions.entity import Order, Product


class TestOrder(TestCase):

    def setUp(self):
        pass

    def test_create_order(self):
        order = Order(order_id="123456")

        order.city = "Москва"
        order.client_name = "Мистер Тест"
        order.client_phone = "+7 (999) 999-9999"

        order.moment = datetime.strptime("02.01.2021 20:06:15", "%d.%m.%Y  %H:%M:%S")
        order.add_product(Product("WCCN80", 6990, 1))

        print(order)


