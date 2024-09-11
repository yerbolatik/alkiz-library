from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from app import settings
from app.conf.media import MEDIA_ROOT, MEDIA_URL
from app.conf.static import STATIC_ROOT, STATIC_URL

api = [
    path("v1/", include("app.urls.v1", namespace="v1")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api)),
    path("bot/", include("tg_bot.urls")),
    path("favorites/", include("favorites.urls")),
    path("books/", include("books.urls")),
    path("users/", include("users.urls")),
    path("rentals/", include("rentals.urls")),
]

if settings.DEBUG:
    urlpatterns += static(STATIC_URL, document_root=STATIC_ROOT)
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
