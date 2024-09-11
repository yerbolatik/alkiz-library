from django.urls import path

from tg_bot import views

app_name = 'tg_bot'

urlpatterns = [
    path("telegram", views.telegram, name='telegram_update'),
    path("submitpayload", views.custom_updates, name="custom_updates"),
    path("healthcheck", views.health, name="health_check"),

    path("", views.startapp, name="startapp"),
    path("index", views.index, name="index"),

    path("login", views.login_user, name="login_user"),
]
