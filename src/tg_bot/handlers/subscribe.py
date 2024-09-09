import logging
from asgiref.sync import sync_to_async
from django.utils import timezone

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from subscriptions.models import Subscription
from tg_bot.context import CustomContext
from users.models import User


logger = logging.getLogger(__name__)


async def show_subscriptions(update: Update, context: CustomContext) -> None:
    """ Offer the user to select a subscription type."""
    keyboard = [
        [InlineKeyboardButton("Monthly (1000 тг)", callback_data='Monthly')],
        [InlineKeyboardButton("Yearly (5000 тг)", callback_data='Yearly')],
        [InlineKeyboardButton("Unlimited (20000 тг)",
                              callback_data='Unlimited')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Выберите тип подписки:",
        reply_markup=reply_markup
    )


async def handle_subscription_choice(update: Update, context: CustomContext):
    """Processes subscription selection and sends payment instructions."""

    query = update.callback_query
    subscription_type = query.data
    telegram_user_id = query.from_user.id

    if subscription_type not in ['Monthly', 'Yearly', 'Unlimited']:
        logger.info(
            f"Получен неподдерживаемый выбор: {subscription_type} от пользователя {telegram_user_id}")
        await query.message.reply_text("Ошибка: Неверный выбор.")
        await query.answer()
        return

    logger.info(
        f"Получен выбор подписки: {subscription_type} от пользователя {telegram_user_id}")

    try:
        user = await sync_to_async(User.objects.get)(telegram_id=telegram_user_id)
    except User.DoesNotExist:
        await query.message.reply_text("Ошибка: Пользователь не найден.")
        return

    existing_subscription = await sync_to_async(Subscription.objects.filter(user=user, active=True).first)()
    if existing_subscription:
        await query.message.reply_text(
            "Ууу вас уже есть активная подписка. \n Для проверки статуса подписки используйте команду /status"
        )
        return

    try:
        subscription = await sync_to_async(Subscription.objects.create)(
            user=user,
            start_date=timezone.now(),
            subscription_type=subscription_type,
            active=False
        )

        logger.info(f"Создана подписка: {subscription.subscription_type}")

    except Exception as e:
        await query.message.reply_text(f"Ошибка подписки: {str(e)}")
        return

    if subscription_type == 'Monthly':
        payment_text = "Спасибо за выбор месячной подписки! Оплатите, пожалуйста 1 000 тг. переводом Каспи на номер +77777777777 Н.Нұрсұлтан."
    elif subscription_type == 'Yearly':
        payment_text = "Спасибо за выбор годовой подписки! Оплатите, пожалуйста 5 000 тг. переводом Каспи на номер +77777777777 Н.Нұрсұлтан."
    elif subscription_type == 'Unlimited':
        payment_text = "Спасибо за выбор неограниченной подписки! Оплатите, пожалуйста 20 000 тг. переводом Каспи на номер +77777777777 Н.Нұрсұлтан."
    else:
        payment_text = "Ошибка: Неверный выбор подписки."

    await query.message.reply_text(payment_text)

    await query.message.delete()

    await query.answer()
    context.chat_data.pop('subscription_choice', None)
    logger.info(
        f"Обработка подписки завершена для пользователя {telegram_user_id}")
