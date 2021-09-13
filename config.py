import os
import logging

# --------------------------------------
CDEK_ACCOUNT = ""
CDEK_SECURE = ""
BOT_TOKEN = ""
# --------------------------------------

CDEK_ACCOUNT = os.environ.get('CDEK_ACCOUNT', CDEK_ACCOUNT)
CDEK_SECURE = os.environ.get('CDEK_SECURE', CDEK_SECURE)
BOT_TOKEN = os.environ.get('BOT_TOKEN', BOT_TOKEN)

logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)