from django.urls import path
from tg_bot.views import telegram, custom_updates, health

urlpatterns = [
    path("telegram", telegram, name="telegram_updates"),
    path("custom_updates", custom_updates, name="custom_updates"),
    path("healthcheck", health, name="healthcheck"),
]
