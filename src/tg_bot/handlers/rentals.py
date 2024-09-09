import logging
from asgiref.sync import sync_to_async
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist


from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes, CallbackContext

from users.models import User
from subscriptions.models import Subscription
from tg_bot.config import TELEGRAM_BOT_TOKEN


logger = logging.getLogger(__name__)


async def send_telegram_message(chat_id, book_title, start_date, end_date, rental_id):
    """
    Отправляет сообщение в Telegram через бот.
    """
    from telegram import Bot

    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    start_date_formatted = start_date.strftime("%d.%m.%Y")
    end_date_formatted = end_date.strftime("%d.%m.%Y")

    message = (
        f"Вы арендовали книгу: {book_title}\n"
        f"Начало аренды: {start_date_formatted}\n"
        f"Конец аренды: {end_date_formatted}"
    )

    inline_keyboard = [
        [
            InlineKeyboardButton(
                'Продлить аренду', callback_data=f'rental_extension:{rental_id}')
        ]
    ]

    await bot.send_message(
        chat_id=chat_id,
        text=message,
        reply_markup=InlineKeyboardMarkup(inline_keyboard),
        parse_mode='HTML'
    )


async def handle_rental_extension(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from rentals.models import Rental, RentalExtension
    """Handle rental extension callback."""
    query = update.callback_query
    data = query.data

    # Сброс ожидания номера телефона или email
    context.user_data.pop('awaiting_email', None)
    context.user_data.pop('data_saved', None)

    # Отладочные сообщения
    print(f"Received callback query data: {data}")

    if data.startswith("rental_extension:"):
        try:
            rental_id = int(data.split(":")[1])
            print(f"Attempting to extend rental with ID: {rental_id}")

            # Логика продления аренды
            rental = await sync_to_async(Rental.objects.get)(id=rental_id)
            if rental:
                extension_count = await sync_to_async(lambda: rental.extensions.count())()
                extension_count += 1
                max_extensions = await sync_to_async(lambda: RentalExtension._DEFAULT_MAX_EXTENSIONS)()

                if extension_count <= max_extensions:
                    rental_extension = RentalExtension(
                        rental=rental,
                        additional_days=7,  # или любое другое значение
                        extension_count=extension_count
                    )
                    await sync_to_async(rental_extension.save)()

                    book = await sync_to_async(lambda: rental.book.title)()
                    end_date_formatted = rental.end_date.strftime("%d.%m.%Y")

                    await query.message.reply_text(f"Аренда успешно продлена.\n"
                                                   f"Книга: {book} \n"
                                                   f"Конец аренды: {end_date_formatted}\n")
                else:
                    await query.message.reply_text("Вы достигли максимального количества продлений.")
            else:
                await query.message.reply_text("Аренда не найдена.")

            await query.answer()

        except ValueError:
            await query.message.reply_text("Ошибка: Неверный идентификатор аренды.")
        except Exception as e:
            print(f"Error handling rental extension: {e}")
            await query.message.reply_text(f"Ошибка: {str(e)}")
