import json
import logging
import config
import telebot

MY_CHAT_ID = "177231333"
bot = telebot.TeleBot(config.BOT_TOKEN)

CDEK_STATUSES = {
    "1": "Создан",
    "2": "Удален",
    "3": "Принят на склад отправителя",
    "6": "Выдан на отправку в г. отправителе",
    "16": "Возвращен на склад отправителя",
    "7": "Сдан перевозчику в г. отправителе",
    "21": "Отправлен в г. транзит",
    "22": "Встречен в г. транзите",
    "13": "Принят на склад транзита",
    "17": "Возвращен на склад транзита",
    "19": "Выдан на отправку в г. транзите",
    "20": "Сдан перевозчику в г. транзите",
    "27": "Отправлен в г. отправитель",
    "8": "Отправлен в г. получатель",
    "28": "Встречен в г. отправителе",
    "9": "Встречен в г. получателе",
    "10": "Принят на склад доставки",
    "12": "Принят на склад до востребования",
    "11": "Выдан на доставку",
    "18": "Возвращен на склад доставки",
    "4": "Вручен",
    "5": "Не вручен"
}

def handler(event, context):
    print("INCOMING_BODY: ", event['body'])

    cdek_msg = json.loads(event['body'])
    cdek_attrs = cdek_msg['attributes']
    cdek_status = cdek_attrs['status_code']
    cdek_status_text = CDEK_STATUSES[cdek_status]

    msg_for_chat = f"Изменение статуса Cdek\n\n" \
                   f"Номер заказа: {cdek_attrs['number']}\n" \
                   f"Номер Cdek: {cdek_attrs['cdek_number']}\n" \
                   f"Статус: {cdek_status_text}\n" \
                   f"Дата: {cdek_attrs['status_date_time']}\n" \
                   f"Город: {cdek_attrs['city_name']}"

    bot.send_message(MY_CHAT_ID, text=msg_for_chat)

    return {
        'statusCode': 200,
        'body': 'OK',
    }

# handler({
#     'body' : '{"type":"ORDER_STATUS","date_time":"2021-09-14T03:55:47+0700","uuid":"72753033-884f-4ab0-8d9d-405dda0fa5ba","attributes":{"is_return":false,"cdek_number":"1275242903","number":"12345","status_code":"1","status_date_time":"2021-09-13T20:55:47+0000","city_name":"Офис СДЭК"}}'
#
# }, None)