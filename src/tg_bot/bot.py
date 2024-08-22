import asyncio
import json
import logging
from uuid import uuid4

import uvicorn
from django.conf import settings
from django.core.asgi import get_asgi_application
from django.core.management.base import BaseCommand

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    TypeHandler,
)

from app.conf.environ import env
from tg_bot.context import CustomContext, WebhookUpdate
from tg_bot.handlers import webhook_update, start
from tg_bot.config import URL, ADMIN_CHAT_ID, PORT

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Define configuration constants
TOKEN = env("TELEGRAM_TOKEN")  # nosec B105


# Set up PTB application and a web application for handling the incoming requests.

context_types = ContextTypes(context=CustomContext)
# Here we set updater to None because we want our custom webhook server to handle the updates
# and hence we don't need an Updater instance
ptb_application = (
    Application.builder().token(TOKEN).updater(
        None).context_types(context_types).build()
)

# register handlers
ptb_application.add_handler(CommandHandler("start", start))
ptb_application.add_handler(TypeHandler(
    type=WebhookUpdate, callback=webhook_update))


# settings.configure(ROOT_URLCONF=__name__, SECRET_KEY=uuid4().hex)


async def main() -> None:
    """Finalize configuration and run the applications."""
    webserver = uvicorn.Server(
        config=uvicorn.Config(
            app=get_asgi_application(),
            port=PORT,
            use_colors=False,
            host="127.0.0.1",
        )
    )

    # Pass webhook settings to telegram
    await ptb_application.bot.set_webhook(url=f"{URL}/telegram", allowed_updates=Update.ALL_TYPES)

    # Run application and webserver together
    async with ptb_application:
        try:
            await ptb_application.start()
            await webserver.serve()
        finally:
            await ptb_application.stop()


if __name__ == "__main__":
    asyncio.run(main())
