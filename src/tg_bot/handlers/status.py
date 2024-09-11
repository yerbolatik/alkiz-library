import logging
import pytz

from asgiref.sync import sync_to_async
from telegram import Update
from tg_bot.context import CustomContext
from subscriptions.models import Subscription
from users.models import User

logger = logging.getLogger(__name__)

FIXED_TIMEZONE = pytz.timezone('Asia/Almaty')


async def status(update: Update, context: CustomContext) -> None:
    """Handle the /status command to show the user's subscription details."""

    telegram_id = update.effective_user.id

    # Try to get the user from the database
    user_queryset = await sync_to_async(User.objects.filter)(telegram_id=telegram_id)
    user = await sync_to_async(user_queryset.first)()

    if user is None:
        await update.message.reply_text("Не удалось найти информацию о подписке. Пожалуйста, выполните команду /start.")
        logger.warning(
            f"User with telegram_id {telegram_id} not found in database.")
        return

    try:
        subscription = await sync_to_async(Subscription.objects.get)(user=user)

        if subscription.is_active():
            start_date = subscription.start_date.astimezone(
                FIXED_TIMEZONE).strftime('%d.%m.%Y %H:%M:%S')
            end_date = subscription.end_date.astimezone(FIXED_TIMEZONE).strftime(
                '%d.%m.%Y %H:%M:%S') if subscription.end_date else 'Не ограничено'

            subscription_info = (
                f"Тип подписки: {subscription.get_subscription_type_display()}\n"
                f"Дата начала: {start_date}\n"
                f"Дата окончания: {end_date}"
            )
        else:
            subscription_info = "Ваша подписка неактивна или завершена."

    except Subscription.DoesNotExist:
        subscription_info = "Подписка не найдена. Пожалуйста, оформите подписку, выполнив команду /subscribe."
        logger.error(
            f"Subscription for user with id {user.id} does not exist.")

    await update.message.reply_text(subscription_info)
