# src/tg_bot/routing.py

from django.urls import path
from . import consumers  # Замените на ваших потребителей

websocket_urlpatterns = [
    # Пример маршрута для WebSocket (замените на ваши маршруты и потребителей)
    # path('ws/some_path/', consumers.MyConsumer.as_asgi()),
]
