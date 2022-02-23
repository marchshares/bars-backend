import typing
from datetime import datetime
from functions import utils

DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


@utils.auto_str
class Product:
    price: float
    quantity: int
    name: str

    def __init__(self, sku: str, price=None, quantity=None, is_service=False):
        self.sku = sku
        self.price = price
        self.quantity = quantity
        self.is_service = is_service

    def get_price(self, x100: bool = False):
        return self.price * (100 if x100 else 1)

    def __repr__(self):
        return str(self)

@utils.auto_str
class Order:
    city: str
    client_name: str
    client_phone: str
    client_email: str
    delivery_company: str
    delivery_address: str = ""
    delivery_client_price: float = 0.0
    delivery_our_price: float = 0.0
    warehouse: str

    payment_system: str = 'cash'
    payment_tax: float = 0.0

    products_price: float
    products: typing.List[Product]

    _moment: datetime

    def __init__(self, order_id: str):
        self.order_id = order_id
        self.products = []

    @property
    def moment(self):
        return self._moment

    @moment.setter
    def moment(self, value):
        if isinstance(value, str):
            value = datetime.fromisoformat(value)

        self._moment = value

    def moment_as_str(self):
        return self._moment.strftime(DATE_TIME_FORMAT)

    def get_delivery_address(self):
        return f"{self.city}, {self.delivery_address}"

    def get_overhead(self, x100: bool = False):
        overhead = (self.delivery_our_price + self.payment_tax)
        return overhead * (100 if x100 else 1)

    def get_overhead_desc(self):
        res = ""

        if self.delivery_our_price > 0:
            res += f"Стоимость доставки: {self.delivery_our_price:.2f}р.\n"

        if self.payment_tax > 0:
            res += f"Комиссия {self.payment_system}: {self.payment_tax:.2f}р.\n"

        return res

    def add_product(self, p: Product):
        self.products.append(p)

    def enrich_product_prices(self, df_with_prices):
        regular_prices = []

        if self.products:
            for p in self.products:
                sku = p.sku
                regular_price = df_with_prices.loc[sku]['old_price']
                if regular_price == 0:
                    regular_price = df_with_prices.loc[sku]['price']

                regular_prices.append(regular_price*p.quantity)

            k = self.products_price / sum(regular_prices)
            for p, regular_price in zip(self.products, regular_prices):
                p.price = k * regular_price / p.quantity

            if len(self.products) > 1:
                s = 0
                for p in self.products:
                    p.price = round(p.price)
                    s += p.price

                last = self.products[-1]
                last.price += self.products_price - s

    def __repr__(self):
        return str(self)


