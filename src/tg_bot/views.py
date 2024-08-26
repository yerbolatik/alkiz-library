import logging
import json

from django.http import JsonResponse, HttpResponse, HttpRequest, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from telegram import Update

from app.asgi import application as web_application
from tg_bot.context import WebhookUpdate

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
