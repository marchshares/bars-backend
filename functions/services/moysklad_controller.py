import logging
from typing import Dict, AnyStr, Optional

from moysklad.queries import Expand, Filter, Query, Search, Select

import config
import pandas as pd
from moysklad.api import MoySklad
from functions.message import Message, OrderStatusMessage
from functions.entity import Order, Product
from functions.services import ServiceController
from functions.utils import none2empty


class MoySkladController(ServiceController):

    def __init__(self) -> None:
        self._client = MoySkladClient(config.MOYSKLAD_LOGIN, config.MOYSKLAD_PASSWORD)

    def consume_request(self, request_body):
        dummy_msg = Message(self.get_name(), {"body": request_body})
        self.publish_message(dummy_msg)

    def consume_message(self, msg: Message):
        if isinstance(msg, OrderStatusMessage):
            order_id = msg.order_id
            order_status = msg.order_status
            self._client.update_order_state(order_id, order_status)


class MoySkladClient():
    DELIVERY_SKU = "DLVR"
    my_organization_id = "67f4100e-daaf-11eb-0a80-06ae00283b54"
    api_project_id = "a1688770-8ce5-11ec-0a80-05e60023f07c"
    attr_delivery_company_id = "6ad182c0-dff9-11eb-0a80-03680022940d"

    __map_order_state_to_href: Dict[AnyStr, AnyStr] = None
    __map_store_to_href: Dict[AnyStr, AnyStr] = None
    __map_product_to_href: Dict[AnyStr, AnyStr] = None
    __map_service_to_href: Dict[AnyStr, AnyStr] = None

    def __init__(self, login, password):
        self._sklad = MoySklad.get_instance(login, password)
        self._http_client = self._sklad.get_client()
        self.endpoint = self._http_client.endpoint
        self.urls = self._sklad.get_methods()

    @property
    def map_order_state_to_href(self):
        if self.__map_order_state_to_href is None:
            self.__map_order_state_to_href = self._get_meta_href_map(
                entity_url=ApiUrls.get_customerorder_metadata_entity_url(),
                data_section_name='states'
            )
            logging.info(f"Lazy loaded order_states_map, size={len(self.map_order_state_to_href)}")

        return self.__map_order_state_to_href

    @property
    def map_store_to_href(self):
        if self.__map_store_to_href is None:
            self.__map_store_to_href = self._get_meta_href_map(
                entity_url=ApiUrls.get_store_entity_url()
            )
            logging.info(f"Lazy loaded stores_map, size={len(self.map_store_to_href)}")

        return self.__map_store_to_href

    @property
    def map_product_to_href(self):
        if self.__map_product_to_href is None:
            self.__map_product_to_href = self._get_meta_href_map(
                entity_url=ApiUrls.get_product_entity_url(),
                key_field_name='article',
                # query=Query(Filter().eq('archived', "true") + Filter().eq('archived', "false"))
            )
            logging.info(f"Lazy loaded products_map, size={len(self.map_product_to_href)}")

        return self.__map_product_to_href

    @property
    def map_service_to_href(self):
        if self.__map_service_to_href is None:
            self.__map_service_to_href = self._get_meta_href_map(
                entity_url=ApiUrls.get_service_entity_url(),
                key_field_name='code',
            )
            logging.info(f"Lazy loaded services_map, size={len(self.map_service_to_href)}")

        return self.__map_service_to_href

    def _get_meta_href_map(self, entity_url: str, data_section_name='rows', key_field_name='name', query: Query=None):
        response = self._http_client.get(
            method=entity_url,
            query=query
        )

        result_map = {}
        for rows in response.data[data_section_name]:
            key = rows[key_field_name]
            href = rows['meta']['href']

            result_map[key] = href

        return result_map

    def get_product_to_price_df(self, query: Query=None) -> pd.DataFrame:
        response = self._http_client.get(
            method=ApiUrls.get_product_entity_url(),
            query=query
        )

        res_arr = []
        for rows in response.data['rows']:
            sku = rows['article']
            prices = rows['salePrices']

            price = prices[0]['value'] / 100
            old_price = 0
            if len(prices) > 1:
                old_price = prices[1]['value'] / 100

            res_arr.append({'sku': sku, 'price': price, 'old_price': old_price})

        return pd.DataFrame(data=res_arr).set_index('sku')

    def get_order_by_ms_order_id(self, ms_order_id: str):
        try:
            response = self._http_client.get(
                method=ApiUrls.get_customerorder_entity_url(id=ms_order_id)
            )

            return response.data
        except Exception as e:
            logging.error(f"Order ms_order_id='{ms_order_id}' wasn't found. Reason: {e}")
            return None

    def get_order_by_order_name(self, order_name: str):
        response = self._http_client.get(
            method=ApiUrls.get_customerorder_entity_url(),
            query=Query(
                Filter().eq('name', order_name),
                Select(1)
            )
        )

        rows = response.data['rows']
        if len(rows) > 0:
            return rows[0]
        else:
            return None

    def get_order_state_by_href(self, val: str):
        for order_state, href in self.map_order_state_to_href.items():
            if val == href:
                return order_state

        return None

    def update_order_state(self, order_name, new_state):
        ms_order = self.get_order_by_order_name(order_name)

        if ms_order is None:
            logging.error(f"Order {order_name} not found. Can't update state for order")
            return

        cur_state = self.get_order_state_by_href(ms_order['state']['meta']['href'])
        if new_state == cur_state:
            logging.info(f"Order '{order_name}' state isn't updated. Already has state={cur_state}")
            return ms_order

        response = self._http_client.put(
            method=ApiUrls.get_customerorder_entity_url(ms_order['id']),
            data={
                'state': {
                    'meta': {
                        'href': self.map_order_state_to_href[new_state],
                        'type': "state"
                    }
                }
            }
        )

        if response.response.ok:
            data = response.data
            logging.info(f"Order '{data['name']}' (ms_order_id='{data['id']}') state updated at '{data['updated']}'")
            return data
        else:
            logging.error(f"Order '{order_name}' state isn't updated. Reason: {response.response.reason}")
            return None

    # ----- Counterparty section -----
    def get_counterparty_by_phone(self, client_phone):
        response = self._http_client.get(
            method=self.urls.get_list_url("counterparty"),
            query=Query(
                Search(client_phone),
                Select(limit=1)
            )
        )
        rows = response.data['rows']
        if len(rows) == 0:
            return None

        return rows[0]

    def find_or_create_counterparty(self, order: Order):
        counterparty = self.get_counterparty_by_phone(order.client_phone)

        if counterparty is not None:
            return counterparty

        response = self._http_client.post(
            method=self.urls.get_create_url("counterparty"),
            data={
                "name": order.client_name,
                "phone": order.client_phone,
                "email": order.client_email,
                "companyType": "individual",
                "tags": ["api", "клиенты интернет-магазинов"]
            }
        )

        if response.response.ok:
            data = response.data
            logging.info(f"Сounterparty '{data['name']}' created at {data['created']}")
        else:
            logging.error(f"Сounterparty {order.client_name} isn't created. Reason: {response.response.reason}")

        return response.data

    # ----- Demand section -----
    def create_demand_template(self, ms_order_id: str):
        response = self._http_client.put(
            method=ApiUrls.get_demand_entity_url() + "/new",
            data={
                "customerOrder": {
                    "meta": {
                        "href": self.endpoint + "/" + ApiUrls.get_customerorder_entity_url(ms_order_id),
                        "type": "customerorder",
                    }
                }
            }
        )

        if response.response.ok:
            data = response.data
            logging.info(f"Demand template for ms_order_id='{ms_order_id}' created")
            return data
        else:
            logging.error(f"Demand template for ms_order_id='{ms_order_id}' isn't created. Reason: {response.response.reason}")
            return None

    def create_demand(self, ms_order_id: str, order: Order):
        data = self.create_demand_template(ms_order_id=ms_order_id)

        # set date created
        data['moment'] = order.moment_as_str()

        # set losses
        overhead = order.get_overhead(x100=True)
        if overhead > 0:
            data['overhead'] = {
                "sum": order.get_overhead(x100=True),
                "distribution": "price"
            }

            data['description'] = none2empty(data.get('description')) + '\n' + order.get_overhead_desc()

        # set API project
        data['project'] = {
            "meta": {
                "href": self.endpoint + "/" + ApiUrls.get_project_entity_url(self.api_project_id),
                "type": "project",
            }
        }

        response = self._http_client.post(
            method=ApiUrls.get_demand_entity_url(),
            data=data
        )

        if response.response.ok:
            data = response.data
            logging.info(f"Demand '{data['name']}' (ms_order_id='{data['id']}') created at '{data['created']}'")
            return data
        else:
            logging.error(f"Demand for ms_order_id='{ms_order_id}' isn't created. Reason: {response.response.reason}")
            return None

    def remove_order_by_order_name(self, order_name: str):
        ms_order = self.get_order_by_order_name(order_name)
        return self.remove_order(ms_order['id'])

    def remove_order(self, ms_order_id: str):
        try:
            self._http_client.delete(
                method=ApiUrls.get_customerorder_entity_url(id=ms_order_id)
            )

            logging.info(f"Order ms_order_id='{ms_order_id}' is removed")
            return True
        except Exception as e:
            logging.error(f"Order ms_order_id='{ms_order_id}' wasn't removed. Reason: {e}")
            return False


    # ----- Order section -----
    def create_order(self, order: Order, state='Новый') -> Optional[Dict]:
        def generate_positions_section():

            # Add delivery client price as separate product
            all_products = order.products.copy()
            if order.delivery_client_price > 0:
                delivery_client_price_as_product = Product(self.DELIVERY_SKU, order.delivery_client_price, 1, is_service=True)
                all_products.append(delivery_client_price_as_product)

            positions = []
            for p in all_products:
                if p.is_service:
                    p_type = "service"
                    p_href = self.map_service_to_href[p.sku]
                else:
                    p_type = "product"
                    p_href = self.map_product_to_href[p.sku]

                positions.append(
                    {
                        "quantity": p.quantity,
                        "price": p.get_price(x100=True),
                        "assortment": {
                            "meta": {
                                "href": p_href,
                                "type": p_type,
                            }
                        }
                    }
                )


            return positions

        # # check order
        # ms_order = self.get_id_by_order_id(order_id=order.order_id)
        # if ms_order is not None:
        #     logging.info(f"Order '{order.order_id}' (ms_order_id='{ms_order['id']}') already exist. Was created at '{ms_order['created']}'")
        #     return ms_order

        counterparty = self.find_or_create_counterparty(order)
        positions_section = generate_positions_section()

        response = self._http_client.post(
            method=ApiUrls.get_customerorder_entity_url(),
            data={
                "name": order.order_id,
                "moment": order.moment_as_str(),
                "shipmentAddress": order.get_delivery_address(),
                "project": {
                    "meta": {
                        "href": self.endpoint + "/" + ApiUrls.get_project_entity_url(self.api_project_id),
                        "type": "project",
                    }
                },
                "organization": {
                    "meta": {
                        "href": self.endpoint + "/" + ApiUrls.get_organization_entity_url(self.my_organization_id),
                        "type": "organization",
                    }
                },
                "agent": {
                    "meta": {
                        "href": self.endpoint + "/" + ApiUrls.get_counterparty_entity_url(counterparty['id']),
                        "type": "counterparty",
                    }
                },
                "store": {
                    "meta": {
                        "href": self.map_store_to_href[order.warehouse],
                        "type": "store",
                    }
                },
                "attributes": [
                    {
                        "meta": {
                            "href": self.endpoint + "/" + ApiUrls.get_customerorder_metadata_attributes_entity_url(
                                self.attr_delivery_company_id),
                            "type": "attributemetadata"
                        },
                        "value": {
                            "name": order.delivery_company
                        }
                    }
                ],
                'state': {
                    'meta': {
                        'href': self.map_order_state_to_href[state],
                        'type': "state"
                    }
                },
                "positions": positions_section
            }
        )

        if response.response.ok:
            data = response.data
            logging.info(f"Order '{data['name']}' (ms_order_id='{data['id']}') created at '{data['created']}'")
            return data
        else:
            logging.error(f"Order '{order.order_id}' isn't created. Reason: {response.response.reason}")
            return None


class ApiUrls:
    @staticmethod
    def get_customerorder_entity_url(id=None):
        if id is not None:
            return f'entity/customerorder/{id}'

        return f'entity/customerorder'

    @staticmethod
    def get_customerorder_metadata_entity_url():
        return f'entity/customerorder/metadata'

    @staticmethod
    def get_demand_entity_url():
        return f'entity/demand'

    @staticmethod
    def get_store_entity_url():
        return f'entity/store'

    @staticmethod
    def get_product_entity_url():
        return f'entity/product'

    @staticmethod
    def get_service_entity_url():
        return f'entity/service'

    @staticmethod
    def get_customerorder_metadata_attributes_entity_url(id=None):
        if id is not None:
            return f'entity/customerorder/metadata/attributes/{id}'

        return f'entity/customerorder/metadata/attributes'

    @staticmethod
    def get_organization_entity_url(id):
        return f'entity/organization/{id}'

    @staticmethod
    def get_counterparty_entity_url(id):
        return f'entity/counterparty/{id}'    \

    @staticmethod
    def get_project_entity_url(id):
        return f'entity/project/{id}'

