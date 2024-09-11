from telegram import Update
from telegram.ext import ContextTypes


async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message to the user using the available commands.."""
    text = (
        "Привет! Вот что я могу сделать:\n\n"
        "/start - Начать работу с ботом.\n"
        "/help - Показать это сообщение.\n"
        "/subscribe - Подписаться на план.\n"
        "/status - Проверить статус вашей подписки."
    )
    await update.message.reply_text(text)
