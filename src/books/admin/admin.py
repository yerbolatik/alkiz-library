from django.contrib import admin

from books.models import Author, Book, Category, Language


class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "publication_date", "available", "average_rating", "rating_count", "rental_count")
    list_filter = ("publication_date", "available")
    search_fields = ("title", "authors__first_name", "authors__last_name")
    ordering = ("-publication_date",)


class AuthorAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "about")
    search_fields = ("first_name", "last_name")


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


class LanguageAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


admin.site.register(Book, BookAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Language, LanguageAdmin)
