from typing import List

import pandas as pd
import config
import logging
import re
from datetime import datetime
from functions.entity import Order, Product
from functions.services.google.google_client import GoogleClient
from functions.services.moysklad_controller import MoySkladClient


class RowToOrderMapper:

    payment_system_map = {
        "yakassa": "yakassa",
        "cash": "cash"
    }

    delivery_company_map = {
        "CDEK":             "Сдек",
        "Грастин":          "Грастин",
        "Самовывоз":        "Самовывоз",
        "Достависта":       "Достависта",
        "ЯндексТакси":      "Достависта",
        "Ontime":           "яя_Ontime",
        "Ontime-CDEK":      "яя_Ontime-CDEK"
    }

    product_name_to_sku_map = {
        "Minipresso GR":                        "WCCMP",
        "Minipresso NS":                        "WCCMPC",
        "Picopresso":                           "WCPPRSS",
        "Nanopresso":                           "WCCN80",
        "Barista Kit":                          "WCCBRST",
        "NS-адаптер":                           "WCCNANS",
        "MP-Чехол":                             "WCCCS",
        "S-Чехол":                              "WCCNSC",
        "M-Чехол":                              "WCCNMC",
        "L-Чехол":                              "WCCNLC",
        "Nanovessel":                           "WCCNNVSL",
        "Nanopresso Elements Chill White":      "WCCCHWH",
        "Nanopresso Elements Moss Green":       "WCCMSGR",
        "Nanopresso Elements Arctic Blue":      "WCCRTCBL",
        "Nanopresso Elements Lava Red":         "WCCLVRD",
        "Nanopresso+NS-адаптер":                "WCCNPA",
        "Minipresso Tank":                      "WCCTNK",
        "Minipresso Kit":                       "WCCKT",
        "Pipamoka":                             "WCCPPMK",
        "Coffee Mat":                           "WCCCFMT",
        "Nanopresso DG Kit":                    "WCCDGK",
        "Pipamoka Чехол":                       "WCCPPMKAC",
        "Nespresso Starbucks Blonde":           "6200797",
        "Nespresso Starbucks Espresso":         "6200697",
        "Nanopresso Journey Winter Ride":       "WCCWTRD",
        "Nanopresso Journey Spring Run":        "WCCSPRN",
        "Nanopresso Journey Summer Session":    "WCCSMSS",
        "Nanopresso Journey Fall Break":        "WCCFLBK",
        "Nanopresso Patrol Yellow":             "WCCN83",
        "Nanopresso Patrol Orange":             "WCCN84",
        "Nanopresso Patrol Red":                "WCCN81",
        "Nanopresso Tattoo Yellow":             "WCCTTTYL",
        "Nanopresso Tattoo Orange":             "WCCTTTOR"

    }

    def map(self, row: pd.Series, products_df: pd.DataFrame) -> Order:
        order = Order(order_id=row['paymentId'])

        order.client_name = row['Name']
        order.client_phone = row['Phone']
        order.client_email = row['Email']
        order.city = row['city']
        order.delivery_address = row['DeliveryAddress']
        order.delivery_company = self.map_delivery_company(row)
        order.delivery_our_price = self.map_price(row['fullDeliveryCost'])
        order.delivery_client_price = self.map_price(row['DeliveryClientCost'], required=False)
        order.warehouse = "Основной склад"

        order.moment = self.map_moment(row)

        order.payment_system = self.map_payment_system(row)
        order.payment_tax = self.map_payment_tax(row)

        order.products_price = self.map_price(row['orderPrice'])

        for idx, product_row in products_df.iterrows():
            product_name = product_row['product']
            product_sku = self.product_name_to_sku_map[product_name]

            order.add_product(
                Product(sku=product_sku, price=None, quantity=int(product_row['quantity']))
            )

        return order

    def map_payment_tax(self, row: pd.Series):
        delivery_client_cost = self.map_price(row['DeliveryClientCost'], required=False)
        order_price = self.map_price(row['orderPrice'])
        total_amount = self.map_price(row['totalAmount'])

        return (order_price+delivery_client_cost) - total_amount

    def map_price(self, price, required=True):
        res = re.sub('[^\d\.]', '', price)

        if res != '':
            return float(res)
        else:
            if required:
                raise Exception(f"map_price: {price}")
            else:
                return 0.0

    def map_moment(self, row: pd.Series):
        dt = row['date'] + " " + row['time']
        return datetime.strptime(dt, "%d.%m.%Y  %H:%M:%S")

    def map_delivery_company(self, row: pd.Series):
        value = self.delivery_company_map.get(row['DeliveryCompany'])
        if not value:
            raise Exception(f"map_delivery_company: {row['DeliveryCompany']}")

        return value

    def map_payment_system(self, row: pd.Series):
        value = self.payment_system_map.get(row['paymentsystem'])
        if not value:
            raise Exception(f"map_payment_system: {row['paymentsystem']}")

        return value


class OrderSyncer:

    def __init__(self) -> None:
        self._ggl_client = GoogleClient(config.GOOGLE_API_CREDENTIALS_PATH)
        self._ms_client = MoySkladClient(config.MOYSKLAD_LOGIN, config.MOYSKLAD_PASSWORD)

    def _load_orders_from_ggl_tables(self, orders_table, products_table) -> List[Order]:
        orders = []
        mapper = RowToOrderMapper()
        for index, order_row in orders_table.iterrows():
            order_id = None

            try:
                order_id = order_row['paymentId']

                if order_row['cancelled'] == 'TRUE':
                    continue

                if order_id not in products_table.index:
                    raise Exception("products not found")

                products_df = products_table.loc[order_id]
                if isinstance(products_df, pd.Series):
                    products_df = products_df.to_frame().T

                order = mapper.map(order_row, products_df)

                orders.append(order)

            except Exception as e:
                logging.error(f"{order_id}: {e}")
        # [logging.info(order) for order in orders]

        orders.sort(key=lambda o: o.moment)

        logging.info(f"Loaded {len(orders)} orders from {orders_table.shape[0]} rows")

        return orders

    @staticmethod
    def filter_by_date_range(orders: List[Order], start: str, end: str):
        start = datetime.strptime(start, "%Y%m%d")
        end = datetime.strptime(end, "%Y%m%d")

        return list(filter(lambda o: start <= o.moment < end, orders))

    def _push_orders_to_moysklad(self, orders: List[Order]):
        orders = OrderSyncer.filter_by_date_range(orders, start="20210101", end="20210201")

        for order in orders:
            ms_order = self._ms_client.create_order(order, state="Доставлен")
            if ms_order is not None:
                self._ms_client.create_demand(ms_order_id=ms_order['id'], order=order)

        # [print(order) for order in orders]
        # print(orders)

    def _enrich_product_prices(self, orders: List[Order]):
        df_with_prices = self._ms_client.get_product_to_price_df()
        for order in orders:
            order.enrich_product_prices(df_with_prices=df_with_prices)

    def sync(self):
        sheets_url = "https://docs.google.com/spreadsheets/d/1Z2tCov-JGWc5Yb6OrySX-5IB8OVsf20t9gU5xQdEYbM"
        # orders_tab_name = "Orders2!1:10"
        orders_tab_name = "Orders2!1:245"
        products_tab_name = "Products2"

        orders_table = self._ggl_client.read(sheets_url, orders_tab_name, first_row_as_header=True)

        products_table = self._ggl_client.read(sheets_url, products_tab_name, first_row_as_header=True)
        products_table.set_index('paymentId', inplace=True)

        orders = self._load_orders_from_ggl_tables(orders_table, products_table)

        self._enrich_product_prices(orders)

        self._push_orders_to_moysklad(orders)


OrderSyncer().sync()