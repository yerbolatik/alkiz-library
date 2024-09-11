from django.contrib import admin
from favorites.models import Favorite


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'created_at')
    list_filter = ('user', 'book')


admin.site.register(Favorite, FavoriteAdmin)
