import pandas as pd
import config
import logging
from functions.entity import Order
from functions.services.google.google_client import GoogleClient
from functions.services.moysklad_controller import MoySkladClient


class RowToOrderMapper:
    delivery_company_map = {
        "CDEK":             "Сдек",
        "Грастин":          "Грастин",
        "Ontime":           "яя_Ontime",
        "Ontime-CDEK":      "яя_Ontime-CDEK",
        "Самовывоз":        "Самовывоз",
        "Достависта":       "Достависта",
        "ЯндексТакси":      "Достависта"
    }

    def map(self, row: pd.Series) -> Order:
        order = Order(order_id=row['paymentId'])

        order.client_name = row['Name']
        order.client_phone = row['Phone']
        order.client_email = row['Email']
        order.city = row['city']
        order.delivery_address = row['DeliveryAddress']
        order.delivery_company = self.map_delivery_company(row)
        # order.delivery_our_price = 450.0
        # order.delivery_client_price = 300.0
        # order.warehouse = "Imsklad"
        # # order.moment = datetime.strptime("02.01.2021 20:06:15", "%d.%m.%Y  %H:%M:%S")
        # # order.moment = datetime.now()
        #
        # order.payment_system = 'yakassa'
        # order.payment_tax = 226.45

        return order

    def map_delivery_company(self, row: pd.Series):
        value = self.delivery_company_map.get(row['DeliveryCompany'])
        if not value:
            raise Exception("map_delivery_company")

        return value


class OrderSyncer:

    def __init__(self) -> None:
        self._ggl_client = GoogleClient(config.GOOGLE_API_CREDENTIALS_PATH)
        # self._ms_client = MoySkladClient(config.MOYSKLAD_LOGIN, config.MOYSKLAD_PASSWORD)

    def sync(self):
        sheets_url = "https://docs.google.com/spreadsheets/d/12gAIjbJdRe23yV8tTs233oOSN_MDXqMy95YUEWr_ogY"
        tab_name = "Orders2!1:10"
        # tab_name = "Orders2"

        orders_table = self._ggl_client.read(sheets_url, tab_name, first_row_as_header=True)

        orders = []
        mapper = RowToOrderMapper()
        for index, row in orders_table.iterrows():
            try:
                order = mapper.map(row)
                orders.append(order)
            except Exception as e:
                logging.error(f"{row['paymentId']}: {e}")

        print(orders)


OrderSyncer().sync()