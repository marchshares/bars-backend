import json
import config
import logging
from datetime import datetime
from random import randint
import pandas as pd
import warnings
from unittest import TestCase, mock

from functions.message.message_publisher import MessagePublisher
from functions.entity import Order, Product
from functions.services.moysklad_controller import MoySkladClient


class MoySkladClientIntTest(TestCase):

    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)
        self.ms_client = MoySkladClient(config.MOYSKLAD_LOGIN, config.MOYSKLAD_PASSWORD)
        self.created_orders = []

    def tearDown(self):
        for orders in self.created_orders:
            self.ms_client.remove_order(orders)

    def test_should_init_maps(self):
        self.assertGreater(len(self.ms_client.map_service_to_href),     0)
        self.assertGreater(len(self.ms_client.map_store_to_href),       0)
        self.assertGreater(len(self.ms_client.map_order_state_to_href), 0)
        self.assertGreater(len(self.ms_client.map_product_to_href),     0)

    def test_should_create_and_remove(self):
        order = self.create_test_order()

        ms_order = self.ms_client.create_order(order)
        self.assertIsNotNone(ms_order)

        result = self.ms_client.remove_order(ms_order['id'])
        self.assertTrue(result)

        ms_order = self.ms_client.get_order_by_ms_order_id(ms_order['id'])
        self.assertIsNone(ms_order)

    def test_should_update(self):
        order = self.create_test_order()

        # create order in ms
        ms_order = self.ms_client.create_order(order)
        cur_state = self.ms_client.get_order_state_by_href(val=ms_order['state']['meta']['href'])

        self.created_orders.append(ms_order['id'])

        # 1. check state - should be Новый
        self.assertEqual(cur_state, "Новый")

        ms_order = self.ms_client.update_order_state(order_name=order.order_id, new_state="Доставлен")
        cur_state = self.ms_client.get_order_state_by_href(val=ms_order['state']['meta']['href'])

        # 2. check state - should be updated - Доставлен
        self.assertEqual(cur_state, "Доставлен")

        ms_order = self.ms_client.update_order_state(order_name=order.order_id, new_state="Доставлен")
        cur_state = self.ms_client.get_order_state_by_href(val=ms_order['state']['meta']['href'])

        # 3. check state - should be the same - Доставлен
        self.assertEqual(cur_state, "Доставлен")

    def create_test_order(self):
        order = Order(order_id=str(randint(100000, 999999)))
        order.client_name = "Мистер Тест"
        order.client_phone = "+7 (999) 999-9999"
        order.city = "Москва"
        order.warehouse = "Imsklad"
        order.delivery_company = "Грастин"
        order.moment = datetime.now()

        return order


