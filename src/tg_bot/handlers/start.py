import html

from telegram import Update
from telegram.ext import ContextTypes

from tg_bot.context import CustomContext
from tg_bot.config import WEBHOOK_URL


async def start(update: Update, context: CustomContext) -> None:
    """Display a message with instructions on how to use this bot."""
    payload_url = html.escape(
        f"{WEBHOOK_URL}/submitpayload?user_id=<your user id>&payload=<payload>")
    text = (
        f"To check if the bot is still running, call <code>{WEBHOOK_URL}/healthcheck</code>.\n\n"
        f"To post a custom update, call <code>{payload_url}</code>."
    )
    await update.message.reply_html(text=text)
