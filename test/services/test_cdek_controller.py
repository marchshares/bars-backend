import json
import config
import logging

from functions.message.message_publisher import MessagePublisher
from functions.services.cdek_controller import CdekController
from unittest import TestCase, mock


class CdekControllerTest(TestCase):

    def setUp(self):
        self.cdek_controller = CdekController()
        self.message_publisher_mock = mock.Mock()

        self.cdek_controller.set_message_publisher(self.message_publisher_mock)
        self.message_publisher_mock.register(self.cdek_controller)

    def test_should_publish(self):
        request_body = json.dumps({"type": "ORDER_STATUS",
                                   "date_time": "2021-09-18T22:00:03+0700",
                                   "uuid": "72753033-a8ea-43df-b7bf-5a588e94cc07",
                                   "attributes": {
                                       "is_return": False,
                                       "cdek_number": "1276728370",
                                       "number_x": "111111111",
                                       "number": "1936881384",
                                       "status_code": "12",
                                       "status_date_time": "2021-09-18T15:00:03+0000",
                                       "city_name": "Офис СДЭК"
                                   }})

        self.cdek_controller.consume_request(request_body)

        self.message_publisher_mock.publish.assert_called()

    def test_should_not_publish(self):
        request_body = json.dumps({"type": "ORDER_STATUS",
                                   "date_time": "2021-09-18T22:00:03+0700",
                                   "uuid": "72753033-a8ea-43df-b7bf-5a588e94cc07",
                                   "attributes": {
                                       "is_return": False,
                                       "cdek_number": "1276728370",
                                       "number_x": "111111111",
                                       "number": "1936881384",
                                       "status_code": "6",
                                       "status_date_time": "2021-09-18T15:00:03+0000",
                                       "city_name": "Офис СДЭК"
                                   }})

        self.cdek_controller.consume_request(request_body)

        self.message_publisher_mock.publish.assert_not_called()



