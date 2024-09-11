import logging
import re
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import MessageHandler, ContextTypes, filters
from asgiref.sync import sync_to_async

from tg_bot.context import CustomContext
from users.models import User


logger = logging.getLogger(__name__)

PHONE_REGEX = re.compile(r'^\+?\d{10,16}$')
EMAIL_REGEX = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')


async def handle_contact(update: Update, context: CustomContext) -> None:
    """Handle the received contact from the user."""

    contact = update.message.contact
    phone_number = contact.phone_number

    await _save_phone_number(update, context, phone_number)


async def handle_text(update: Update, context: CustomContext) -> None:
    """Handle text messages that may contain a phone number or email."""

    if context.user_data.get('data_saved', False):
        return

    text = update.message.text

    if context.user_data.get('awaiting_email'):
        if EMAIL_REGEX.match(text):
            await _save_email(update, context, text)
        else:
            await update.message.reply_text("Пожалуйста, отправьте email в правильном формате.")
            logger.info(f"Invalid email format received: {text}")

    else:
        if PHONE_REGEX.match(text):
            await _save_phone_number(update, context, text)
        else:
            await update.message.reply_text("Пожалуйста, отправьте номер телефона в правильном формате.")
            logger.info(f"Invalid phone number format received: {text}")


async def _save_phone_number(update: Update, context: CustomContext, phone_number: str) -> None:
    """Saving a phone number to a user profile."""
    try:
        user = await sync_to_async(User.objects.get)(telegram_id=update.effective_user.id)
        user.phone_number = phone_number
        await sync_to_async(user.save)()
        await update.message.reply_text("Спасибо за ваш номер телефона. Пожалуйста, отправьте ваш email.", reply_markup=ReplyKeyboardRemove())

        # Установка режима ожидания email
        # Если вы используете такое состояние
        # context.user_data['awaiting_phone'] = False
        context.user_data['awaiting_email'] = True
        # context.user_data['data_saved'] = True
        logger.info(f"User {update.effective_user.id} awaiting email.")

    except User.DoesNotExist:
        await update.message.reply_text("Ошибка: Пользователь не найден.")
        logger.error(f"User {update.effective_user.id} does not exist.")


async def _save_email(update: Update, context: CustomContext, email: str) -> None:
    """Saving an email to a user profile."""
    try:
        user = await sync_to_async(User.objects.get)(telegram_id=update.effective_user.id)
        user.email = email
        await sync_to_async(user.save)()
        await update.message.reply_text(f"Спасибо за ваш email: {email}")

        # Очистка состояния ожидания email
        context.user_data['awaiting_email'] = False
        context.user_data['data_saved'] = True

        logger.info(f"User {update.effective_user.id} email saved.")

        await update.message.reply_text("Все данные успешно сохранены. Вы можете начать использовать бота. \n\nВы можете использовать команду /subscribe для оформления подписки и команду /status для проверки статуса подписки.")

    except User.DoesNotExist:
        await update.message.reply_text("Ошибка: Пользователь не найден.")
        logger.error(f"User {update.effective_user.id} does not exist.")
