from django.contrib import admin

from subscriptions.models import Subscription


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "start_date", "end_date",
                    "active", "subscription_type")
    ordering = ("-id",)
    list_filter = ("active", "subscription_type")
    search_fields = ("user__email", "user__first_name", "user__last_name")
    ordering = ("-start_date",)


admin.site.register(Subscription, SubscriptionAdmin)
