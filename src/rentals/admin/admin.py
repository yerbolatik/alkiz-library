from django.contrib import admin
from django.utils import timezone

from rentals.models import Rental, RentalExtension


class RentalAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "start_date", "end_date", "returned")
    ordering = ("-id",)
    list_filter = ("returned", "start_date", "end_date")
    search_fields = ("user__username", "book__title")
    readonly_fields = ("start_date",)
    fields = ("user", "book", "start_date", "end_date", "returned")

    def save_model(self, request, obj, form, change):
        if obj.returned:
            obj.book.available = True
            obj.end_date = timezone.now()
            obj.book.save()
        super().save_model(request, obj, form, change)


class RentalExtensionAdmin(admin.ModelAdmin):
    list_display = ("rental", "extension_date",
                    "additional_days", "extension_count")
    search_fields = ("rental__book__title", "rental__user__username")
    readonly_fields = ("extension_date", "extension_count")
    fields = ("rental", "extension_date", "additional_days", "extension_count")


admin.site.register(Rental, RentalAdmin)
admin.site.register(RentalExtension, RentalExtensionAdmin)
