import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    TypeHandler,
    MessageHandler,
    filters,
)
from tg_bot.config import TELEGRAM_BOT_TOKEN, WEBHOOK_URL
from tg_bot.context import CustomContext, WebhookUpdate
from tg_bot.handlers import (
    start, handle_contact, handle_text,
    show_subscriptions, handle_subscription_choice,
    handle_help,
    status,
    handle_rental_extension,
)
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
    help_handler = CommandHandler('help', handle_help)

    handle_contact_handler = MessageHandler(filters.CONTACT, handle_contact)
    handle_text_handler = MessageHandler(
        filters.TEXT & (~filters.COMMAND), handle_text)

    subscribe_handler = CommandHandler('subscribe', show_subscriptions)
    status_handler = CommandHandler('status', status)
    rental_extension_handler = CallbackQueryHandler(
        handle_rental_extension, pattern=r'^rental_extension:')
    handle_subscription_choice_handler = CallbackQueryHandler(
        handle_subscription_choice)

    application.add_handler(start_handler)
    application.add_handler(help_handler)

    application.add_handler(handle_contact_handler)
    application.add_handler(handle_text_handler)

    application.add_handler(rental_extension_handler)

    application.add_handler(subscribe_handler)
    application.add_handler(status_handler)
    application.add_handler(handle_subscription_choice_handler)

    application.add_handler(TypeHandler(
        type=WebhookUpdate, callback=webhook_update))

    # Pass webhook settings to telegram
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/bot/telegram", allowed_updates=Update.ALL_TYPES)

    return application
