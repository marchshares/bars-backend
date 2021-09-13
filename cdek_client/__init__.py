import logging
import config
import os
import requests
from cdek.api import *


class CdekClientWrapper(CDEKClient):
    AUTH_URL = "https://api.cdek.ru/v2/oauth/token?parameters"
    WEBHOOKS_URL = "https://api.cdek.ru/v2/webhooks"

    def __init__(self):
        self._account = config.CDEK_ACCOUNT
        self._secure = config.CDEK_SECURE
        self._access_token = self._get_access_token()
        super().__init__(self._account, self._secure)

    def _get_access_token(self):
        response = requests.post(
            url=self.AUTH_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": self._account,
                "client_secret": self._secure
            }
        )
        response.raise_for_status()

        logging.info("Token received")
        return response.json()['access_token']

    def check_subscriptions(self):
        response = requests.get(
            url=self.WEBHOOKS_URL,
            headers={
                'Authorization': 'Bearer ' + self._access_token
            }
        )
        response.raise_for_status()

        subs = response.json()
        logging.info("Current subscriptions: " + str(subs))

        return [sub["uuid"] for sub in subs]

    def add_subscription(self, url):
        response = requests.post(
            url=self.WEBHOOKS_URL,
            headers={
                'Authorization': 'Bearer ' + self._access_token
            },
            json={
                "url": url,
                "type": "ORDER_STATUS"
            }
        )

        if response.status_code != 200:
            logging.error(f"Subscription not added. Code: {response.status_code}, Text: {response.text}")
            raise Exception()

        logging.info("Subscription added: " + response.text)

    def remove_all_subscriptions(self):
        sub_uuids = self.check_subscriptions()
        remaining = sub_uuids.copy()
        for uuid in sub_uuids:
            response = requests.delete(
                url=self.WEBHOOKS_URL + "/" + uuid,
                headers={
                    'Authorization': 'Bearer ' + self._access_token
                }
            )

            if response.ok:
                remaining.remove(uuid)
            else:
                logging.error(f"Can't remove subscription (uuid={uuid}). Reason: {response.reason}")

        all_count = len(sub_uuids)
        removed_count = all_count - len(remaining)

        logging.info(f"Removed subs {removed_count / all_count}")

        if len(remaining) != 0:
            logging.error("Not removed subs" + str(remaining))

        return remaining


    def get_cdek_id_by_order_id(self, order_id: str) -> List[Dict]:
        status_report_element = ElementTree.Element(
            'StatusReport',
            ShowHistory=0
        )

        ElementTree.SubElement(
            status_report_element,
            'Order',
            Number=order_id,
            DateFirst="2021-07-20"
        )

        xml = self._exec_xml_request(
            url=self.ORDER_STATUS_URL,
            xml_element=status_report_element,
        )

        return [xml_to_dict(order) for order in xml.findall('Order')]
