import logging
from typing import Dict, AnyStr

from moysklad.queries import Expand, Filter, Ordering, Select, Search, Query

import config
from moysklad.api import MoySklad
from functions.message import Message, OrderStatusMessage
from functions.services import ServiceController


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
    map_order_state_to_href: Dict[AnyStr, AnyStr]

    def __init__(self, login, password):
        self._sklad = MoySklad.get_instance(login, password)
        self._client = self._sklad.get_client()
        self.map_order_state_to_href = self.get_order_states_map()

    def get_order_states_map(self):
        response = self._client.get(
            method=MoySkladClient.get_customerorder_metadata_entity_url(),
        )

        result_map = {}
        for state in response.data['states']:
            state_name = state['name']
            href = state['meta']['href']

            result_map[state_name] = href

        return result_map

    def get_id_by_order_id(self, order_id):
        response = self._client.get(
            method=(MoySkladClient.get_customerorder_entity_url()),
            query=Query(
                Filter().eq('name', order_id)
            )
        )

        rows = response.data['rows']
        if len(rows) > 0:
            return rows[0]['id']
        else:
            return None

    def get_customer_order_by_order_id(self, order_id):
        id = self.get_id_by_order_id(order_id)
        if id is None:
            return None

        response = self._client.get(
            method=(MoySkladClient.get_customerorder_entity_url(id)),
            query=Query(
                Expand('state')
            )
        )

        return response.data

    def update_order_state(self, order_id, new_state):
        customer_order = self.get_customer_order_by_order_id(order_id)

        if customer_order is None:
            logging.error(f"Order {order_id} not found. Can't update state for order")
            return

        old_state = customer_order['state']['name']
        if new_state != old_state:
            new_state_href = self.map_order_state_to_href[new_state]

            self._client.put(
                method=MoySkladClient.get_customerorder_entity_url(customer_order['id']),
                data={
                    'state': {
                        'meta': {
                            'href': new_state_href,
                            'type': "state"
                        }
                    }
                }
            )

    @staticmethod
    def get_customerorder_entity_url(id=None):
        if id is not None:
            return f'entity/customerorder/{id}'

        return f'entity/customerorder'


    @staticmethod
    def get_customerorder_metadata_entity_url():
        return f'entity/customerorder/metadata'