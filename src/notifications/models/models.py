from app.conf.auth import AUTH_USER_MODEL
from app.models import models
from users.mixins import TimestampMixin


class NotificationType(TimestampMixin, models.Model):
    """
    Тип уведомления.

    Атрибуты:
    - name: Название типа уведомления (уникально).
    - description: Описание типа уведомления (необязательно).

    Методы:
    - __str__: Возвращает название типа уведомления в виде строки.
    """

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class NotificationManager(models.Manager):
    """
    Менеджер для управления уведомлениями.

    Методы:
    - unread_notifications: Возвращает непрочитанные уведомления для указанного пользователя.
    - mark_all_as_read: Отмечает все уведомления как прочитанные для указанного пользователя.
    """

    def unread_notifications(self, user):
        return self.filter(user=user, read=False)

    def mark_all_as_read(self, user):
        return self.filter(user=user, read=False).update(read=True)


class Notification(TimestampMixin, models.Model):
    """
    Уведомление для пользователя.

    Атрибуты:
    - user: Пользователь, которому принадлежит уведомление (ForeignKey).
    - message: Сообщение уведомления.
    - read: Статус прочтения уведомления.
    - notification_type: Тип уведомления (ForeignKey, необязательно).

    Методы:
    - __str__: Возвращает строку с уведомлением для пользователя.
    """

    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    read = models.BooleanField(default=False)
    notification_type = models.ForeignKey(
        "NotificationType", on_delete=models.SET_NULL, null=True, related_name="notifications")

    objects = NotificationManager()

    def __str__(self):
        return f"Notification for {self.user.username}"
