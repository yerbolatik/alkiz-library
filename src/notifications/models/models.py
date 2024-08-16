from app.conf.auth import AUTH_USER_MODEL
from app.models import models
from users.mixins import TimestampMixin


class NotificationType(TimestampMixin, models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Notification(TimestampMixin, models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    read = models.BooleanField(default=False)
    notification_type = models.ForeignKey("NotificationType", on_delete=models.SET_NULL, null=True, related_name="notifications")

    def __str__(self):
        return f"Notification for {self.user.username}"
