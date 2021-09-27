import os
import logging

# --------------------------------------
CDEK_ACCOUNT = ""
CDEK_SECURE = ""
BOT_TOKEN = ""
BOT_CHAT_ID = ""
MOYSKLAD_LOGIN = ""
MOYSKLAD_PASSWORD = ""
SMSAERO_LOGIN = ""
SMSAERO_PASSWORD = ""
# --------------------------------------

CDEK_ACCOUNT = os.environ.get('CDEK_ACCOUNT', CDEK_ACCOUNT)
CDEK_SECURE = os.environ.get('CDEK_SECURE', CDEK_SECURE)
BOT_TOKEN = os.environ.get('BOT_TOKEN', BOT_TOKEN)
BOT_CHAT_ID = os.environ.get('BOT_CHAT_ID', BOT_CHAT_ID)
MOYSKLAD_LOGIN = os.environ.get('MOYSKLAD_LOGIN', MOYSKLAD_LOGIN)
MOYSKLAD_PASSWORD = os.environ.get('MOYSKLAD_PASSWORD', MOYSKLAD_PASSWORD)
SMSAERO_LOGIN = os.environ.get('SMSAERO_LOGIN', SMSAERO_LOGIN)
SMSAERO_PASSWORD = os.environ.get('SMSAERO_PASSWORD', SMSAERO_PASSWORD)

IS_LOCAL = os.environ.get('USERNAME') is not None

# logging
logging.getLogger().setLevel(logging.INFO)

if IS_LOCAL:
    logging.basicConfig(format='[%(levelname)s] %(asctime)s: %(module)-20s%(message)s')
else:
    root_handler = logging.getLogger().handlers[0]
    root_handler.setFormatter(
        logging.Formatter('[%(levelname)s] %(asctime)s: [%(request_id)s] %(module)-20s%(message)s')
    )
