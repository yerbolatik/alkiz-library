import logging
import json

from asgiref.sync import sync_to_async
from django.contrib.auth import login, get_user_model
from django.contrib.auth.backends import ModelBackend
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpRequest, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from telegram import Update

from app.asgi import application as web_application
from books.models import Book, Category
from rentals.models import Rental
from reviews.models import Rating, Review
from tg_bot.context import WebhookUpdate
from users.models import User

logger = logging.getLogger(__name__)


async def telegram(request: HttpRequest) -> HttpResponse:
    """Handle incoming Telegram updates by putting them into the `update_queue`"""
    print(request.body, '*******')
    await web_application.tg_application.update_queue.put(Update.de_json(data=json.loads(request.body), bot=web_application.tg_application.bot))
    return JsonResponse({"status": "ok"})


async def custom_updates(request: HttpRequest) -> HttpResponse:
    """
    Handle incoming webhook updates by also putting them into the `update_queue` if
    the required parameters were passed correctly.
    """
    try:
        user_id = int(request.GET["user_id"])
        payload = request.GET["payload"]
    except KeyError:
        return HttpResponseBadRequest(
            "Please pass both `user_id` and `payload` as query parameters.",
        )
    except ValueError:
        return HttpResponseBadRequest("The `user_id` must be a string!")

    await web_application.tg_application.update_queue.put(WebhookUpdate(user_id=user_id, payload=payload))
    return HttpResponse()


async def health(_: HttpRequest) -> HttpResponse:
    """For the health endpoint, reply with a simple plain text message."""
    return HttpResponse("The bot is still running fine :)")


async def startapp(request):
    return render(request, 'tg_bot/startapp.html')


def login_user(request):
    if request.method == 'POST':
        telegram_id = request.POST.get('user_id')
        username = request.POST.get('user_name')

        if not telegram_id or not username:
            return HttpResponseBadRequest("Telegram ID and username are required.")

        # Найти или создать пользователя
        user, created = User.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={'username': username}
        )

        if created:
            user.set_unusable_password()  # Или установите пароль по вашему выбору
            user.save()

        backend = 'django.contrib.auth.backends.ModelBackend'

        login(request, user, backend=backend)
        return redirect('tg_bot:index')  # Или другую страницу по вашему выбору

    return HttpResponseBadRequest("Invalid request method.")


async def handle_callback_query(request: HttpRequest) -> HttpResponse:
    """Handle callback queries from InlineKeyboardButton presses."""
    if request.method == "POST":
        data = json.loads(request.body)
        callback_data = data.get("callback_query", {}).get("data")
        user_id = data.get("callback_query", {}).get("from", {}).get("id")

        if callback_data and user_id:
            user_model = get_user_model()
            user, created = await sync_to_async(user_model.objects.get_or_create)(telegram_id=user_id)

            if created:
                logger.info(f"New user created: {user}")
            else:
                logger.info(f"Existing user found: {user}")

            # Process the callback data
            if callback_data.startswith("rate"):
                try:
                    _, book_id, score = callback_data.split(":")
                    book_id = int(book_id)  # Ensure book_id is an integer
                    score = int(score)

                    # Ensure book exists before updating or creating a rating
                    book = await sync_to_async(Book.objects.get)(id=book_id)

                    await sync_to_async(Rating.objects.update_or_create)(
                        user=user, book=book, defaults={'score': score}
                    )
                    logger.info(
                        f"User {user} rated book {book_id} with score {score}")
                except (ValueError, Book.DoesNotExist) as e:
                    logger.error(f"Error processing rating: {e}")

            # Handle other callback data scenarios if needed
            return JsonResponse({"status": "ok"})

    return HttpResponse(status=400)


async def index(request):
    books = await sync_to_async(list)(Book.objects.all())

    categories = await sync_to_async(list)(Category.objects.all())

    book_authors = []
    for book in books:
        authors = await sync_to_async(list)(book.authors.all())
        language = await sync_to_async(lambda: book.language)()
        average_rating = await sync_to_async(Rating.objects.average_rating_for_book)(book)
        categories = await sync_to_async(list)(book.categories.all())
        book_authors.append({
            'book': book,
            'authors': authors,
            'language': language,
            'categories': categories,
            'average_rating': average_rating,
        })

    top_renters = await sync_to_async(list)(Rental.objects.top_renters(limit=10))

    context = {
        "books": book_authors,
        "categories": categories,
        "top_renters": top_renters,
    }

    return render(request, 'tg_bot/index.html', context)
