# src\tg_bot\config.py
from app.conf.environ import env

ADMIN_CHAT_ID = env('ADMIN_CHAT_ID')
WEBHOOK_URL = env('WEBHOOK_URL')
PORT = env('NGROK_PORT')
TELEGRAM_BOT_TOKEN = env('TELEGRAM_BOT_TOKEN')
