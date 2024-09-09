import asyncio
from asyncio.log import logger

from datetime import timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from app.conf.auth import AUTH_USER_MODEL
from app.models import models
from subscriptions.models.choices import SUBSCRIPTION_CHOICES
from users.mixins import TimestampMixin
from users.models import User


class SubscriptionManager(models.Manager):
    """
    Менеджер для управления подписками.

    Методы:
    - create: Создает подписку, проверяя наличие активной подписки у пользователя.
    """

    def create(self, **kwargs):
        user = kwargs.get('user')
        if self.filter(user=user, active=True).exists():
            raise ValueError(
                "У вас уже есть активная подписка. \n\n Для проверки статуса подписки используйте команду /status")
        return super().create(**kwargs)


class Subscription(TimestampMixin, models.Model):
    """
    Подписка пользователя на систему.

    Атрибуты:
    - user: Пользователь, который подписан (OneToOneField).
    - start_date: Дата начала подписки.
    - end_date: Дата окончания подписки (необязательно).
    - active: Статус активности подписки.
    - subscription_type: Тип подписки (выбор из предопределенных типов).

    Методы:
    - save: Устанавливает дату окончания подписки в зависимости от типа.
    - is_active: Проверяет, активна ли подписка.
    - __str__: Возвращает строку с информацией о подписке.
    """

    user = models.OneToOneField(
        AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscription")
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=False)
    subscription_type = models.CharField(
        max_length=100, choices=SUBSCRIPTION_CHOICES, default="Monthly")

    objects = SubscriptionManager()

    def save(self, *args, **kwargs):
        if self.start_date:
            if self.subscription_type == "Monthly":
                self.end_date = self.start_date + timedelta(days=30)
            elif self.subscription_type == "Yearly":
                self.end_date = self.start_date + timedelta(days=365)
            elif self.subscription_type == "Unlimited":
                self.end_date = None
        super().save(*args, **kwargs)

        if self.active and not self.pk:
            try:
                user = User.objects.get(id=self.user.id)
                message = "Спасибо за оплату! Можете начинать пользоваться приложением."
                from tg_bot.handlers.notify_user import notify_user_about_subscription

                asyncio.run(notify_user_about_subscription(
                    user.telegram_id, message))
            except User.DoesNotExist:
                logger.error(
                    f"User {self.user.id} does not exist for subscription notification.")

    def is_active(self):
        if self.subscription_type == "Unlimited":
            return self.active
        return self.active and self.end_date >= timezone.now()

    def __str__(self):
        return f"Subscription for {self.user.username}, Type: {self.get_subscription_type_display()}"


@receiver(post_save, sender=Subscription)
def subscription_post_save(sender, instance, **kwargs):
    if instance.active:
        from tg_bot.handlers.notify_user import notify_user_about_subscription

        asyncio.run(notify_user_about_subscription(instance.user.telegram_id,
                    "Спасибо за оплату! Можете начинать пользоваться приложением."))
