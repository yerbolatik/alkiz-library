import html

from asgiref.sync import sync_to_async
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove

from tg_bot.context import CustomContext
from users.models import User


async def start(update: Update, context: CustomContext) -> None:
    """Display a message with instructions on how to use this bot and ask for phone number."""

    telegram_id = update.effective_user.id
    telegram_username = update.effective_user.username

    user, created = await sync_to_async(User.objects.get_or_create)(
        telegram_id=telegram_id,
        defaults={
            'telegram_username': telegram_username,
            'username': telegram_username,
            'telegram_id': telegram_id,
        }
    )

    if not created:
        user.telegram_username = telegram_username
        await sync_to_async(user.save)()

    # Save user id to context for further steps
    context.user_data['user_id'] = user.id

    if user.phone_number:
        text = (
            "Добро пожаловать обратно! Вы можете использовать команду /subscribe для оформления подписки "
            "и команду /status для проверки статуса подписки."
        )
        reply_markup = ReplyKeyboardRemove()

    else:
        # Пользователь новый - показываем кнопку "Поделиться телефоном"
        text = (
            "Пожалуйста, поделитесь номером телефона, нажав на кнопку \"Поделиться телефоном\" или напишите вручную."
        )
        keyboard = [
            [
                KeyboardButton("Поделиться телефоном", request_contact=True)
            ]
        ]
        reply_markup = ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_html(text=text, reply_markup=reply_markup)
