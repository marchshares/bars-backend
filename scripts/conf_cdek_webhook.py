import logging
import config
import cdek_client

# NOTIFICATIONS_ENDPOINT = "https://8bars.requestcatcher.com"
NOTIFICATIONS_ENDPOINT = "https://d5djij9bsgsgla82pqga.apigw.yandexcloud.net/cdek-notification"

client = cdek_client.CdekClientWrapper()
client.add_subscription(NOTIFICATIONS_ENDPOINT)
client.check_subscriptions()




