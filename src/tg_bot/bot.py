import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, TypeHandler

from tg_bot.config import TELEGRAM_BOT_TOKEN, WEBHOOK_URL
from tg_bot.context import CustomContext, WebhookUpdate
from tg_bot.handlers import start, echo, caps
from tg_bot.webhook_update import webhook_update


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def get_application() -> None:
    """Set up the application and a custom webserver."""
    context_types = ContextTypes(context=CustomContext)
    application = (
        Application.builder().token(TELEGRAM_BOT_TOKEN).updater(
            None).context_types(context_types).build()
    )

    start_handler = CommandHandler('start', start)

    application.add_handler(start_handler)
    application.add_handler(TypeHandler(
        type=WebhookUpdate, callback=webhook_update))

    # Pass webhook settings to telegram
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/telegram", allowed_updates=Update.ALL_TYPES)

    return application
