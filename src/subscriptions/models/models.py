from datetime import timedelta

from django.utils import timezone

from app.conf.auth import AUTH_USER_MODEL
from app.models import models
from subscriptions.models.choices import SUBSCRIPTION_CHOICES
from users.mixins import TimestampMixin


class Subscription(TimestampMixin, models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscription")
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=False)
    subscription_type = models.CharField(max_length=100, choices=SUBSCRIPTION_CHOICES, default="Monthly")

    def save(self, *args, **kwargs):
        if self.start_date:
            if self.subscription_type == "Monthly":
                self.end_date = self.start_date + timedelta(days=30)
            elif self.subscription_type == "Yearly":
                self.end_date = self.start_date + timedelta(days=365)
            elif self.subscription_type == "Unlimited":
                self.end_date = None
        super().save(*args, **kwargs)

    def is_active(self):
        if self.subscription_type == "Unlimited":
            return self.active
        return self.active and self.end_date >= timezone.now()

    def __str__(self):
        return f"Subscription for {self.user.username}, Type: {self.get_subscription_type_display()}"
