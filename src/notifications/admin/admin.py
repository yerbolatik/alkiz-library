from django.contrib import admin

from notifications.models import Notification, NotificationType


class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "message", "created_at", "read")
    search_fields = ("user__username", "message")
    list_filter = ("read",)


class NotificationTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "description")


admin.site.register(Notification, NotificationAdmin)
admin.site.register(NotificationType, NotificationTypeAdmin)
