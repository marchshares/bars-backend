import logging
import config

from functions.message.message_publisher import MessagePublisher
from functions.services.dummy_controller import DummyController



def handler(event, context):
    body = event['body']
    logging.info("INCOMING_BODY: %s", body)

    dc = controllers[0]
    dc.consume_request(body)

controllers = [
    DummyController()
]

publisher = MessagePublisher()
for c in controllers:
    c.set_message_publisher(publisher)
    publisher.register(c)


handler({
    "body": "Hi!"
}, None)







