from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import CallbackContext

from tg_bot.config import TELEGRAM_BOT_TOKEN, WEBHOOK_URL


async def notify_user_about_subscription(user_id: int, message: str) -> None:
    """Sends a message to the user to confirm payment for the subscription."""
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    try:
        keyboard = [
            [InlineKeyboardButton(
                text="Библиотека 📚",
                web_app=WebAppInfo(url=f"{WEBHOOK_URL}/bot/"))]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await bot.send_message(
            chat_id=user_id,
            text=message,
            reply_markup=reply_markup
        )

    except Exception as e:
        print(f"Ошибка при отправке сообщения пользователю: {e}")
