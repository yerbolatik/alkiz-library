from django.urls import path

from tg_bot import views

urlpatterns = [
    path("telegram", views.telegram, name='telegram_update'),
    path("submitpayload", views.custom_updates, name="custom_updates"),
    path("healthcheck", views.health, name="health_check"),
]
