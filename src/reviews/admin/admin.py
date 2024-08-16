from django.contrib import admin

from reviews.models import Rating, Review


class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "review_text", "created_at")
    search_fields = ("user__username", "book__title")
    list_filter = ("book",)


class RatingAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "score", "created_at")
    search_fields = ("user__username", "book__title")
    list_filter = ("book",)


admin.site.register(Review, ReviewAdmin)
admin.site.register(Rating, RatingAdmin)
