import telebot
import config

WEBHOOK_URL = "d5djij9bsgsgla82pqga.apigw.yandexcloud.net"

bot = telebot.TeleBot(config.BOT_TOKEN)

bot.remove_webhook()
bot.set_webhook(WEBHOOK_URL)