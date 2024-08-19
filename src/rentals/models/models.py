from datetime import timedelta
from django.db.models import Count

from app.conf.auth import AUTH_USER_MODEL
from app.models import models
from books.models import Book
from subscriptions.models import Subscription
from users.mixins import TimestampMixin


class RentalManager(models.Manager):
    """
    Менеджер для управления арендой книг.

    Методы:
    - create: Создает аренду, проверяя наличие активной подписки и статус книги.
    """

    def create(self, **kwargs):
        user = kwargs.get('user')
        book = kwargs.get('book')

        if not Subscription.objects.filter(user=user, active=True).exists():
            raise ValueError(
                "User must have an active subscription to rent a book.")

        if self.filter(user=user, returned=False).exists():
            raise ValueError("User already has an active rental.")

        if self.filter(book=book, returned=False).exists():
            raise ValueError("Book is already rented out.")

        super().create(**kwargs)

    def top_renters(self, limit=10):
        return self.values('user').annotate(
            total_rentals=Count('id')
        ).order_by('-total_rentals')[:limit]


class Rental(TimestampMixin, models.Model):
    """
    Аренда книги пользователем.

    Атрибуты:
    - user: Пользователь, арендующий книгу (ForeignKey).
    - book: Книга, которая арендуется (ForeignKey).
    - start_date: Дата начала аренды.
    - end_date: Дата окончания аренды.
    - returned: Статус возврата книги.

    Методы:
    - save: Устанавливает дату окончания аренды по умолчанию (14 дней).
    - mark_as_returned: Отмечает книгу как возвращенную и делает ее доступной.
    - __str__: Возвращает строку с деталями аренды книги.
    """

    user = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rentals")
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="rentals")
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    returned = models.BooleanField(default=False)

    objects = RentalManager()

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.start_date + timedelta(days=14)
        super().save(*args, **kwargs)

    def mark_as_returned(self):
        self.returned = True
        self.book.available = True
        self.save()

    def __str__(self):
        return f"Rental of {self.book.title} by {self.user.last_name} {self.user.first_name}"


class RentalExtension(TimestampMixin, models.Model):
    """
    Продление аренды книги.

    Атрибуты:
    - rental: Аренда, которую продлевают (ForeignKey).
    - extension_date: Дата продления.
    - additional_days: Дополнительные дни аренды.
    - extension_count: Количество продлений.

    Методы:
    - save: Обновляет дату окончания аренды и проверяет максимальное количество продлений.
    - get_max_extensions: Возвращает максимальное количество продлений.
    - __str__: Возвращает строку с деталями продления аренды книги.
    """

    rental = models.ForeignKey(
        Rental, on_delete=models.CASCADE, related_name="extensions")
    extension_date = models.DateTimeField(auto_now_add=True)
    additional_days = models.PositiveIntegerField(default=7)
    extension_count = models.PositiveIntegerField()

    _DEFAULT_MAX_EXTENSIONS = 2

    def save(self, *args, **kwargs):
        max_extensions = self.get_max_extensions()

        if not self.pk:
            last_extension = RentalExtension.objects.filter(
                rental=self.rental).order_by("-extension_count").first()
            self.extension_count = last_extension.extension_count + 1 if last_extension else 1

        if self.extension_count <= max_extensions:
            self.rental.end_date += timedelta(days=self.additional_days)
            self.rental.save()
            super().save(*args, **kwargs)
        else:
            raise ValueError("Maximum number of extensions reached")

    def get_max_extensions(self):
        return self._DEFAULT_MAX_EXTENSIONS

    def __str__(self):
        return f"Extension {self.extension_count} for {self.rental.book.title} by {self.rental.user.username} on {self.extension_date}"
