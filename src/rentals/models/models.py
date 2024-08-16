from datetime import timedelta

from app.conf.auth import AUTH_USER_MODEL
from app.models import models
from books.models import Book
from users.mixins import TimestampMixin


class Rental(TimestampMixin, models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rentals")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="rentals")
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    returned = models.BooleanField(default=False)

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
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name="extensions")
    extension_date = models.DateTimeField(auto_now_add=True)
    additional_days = models.PositiveIntegerField(default=7)
    extension_count = models.PositiveIntegerField()

    _DEFAULT_MAX_EXTENSIONS = 2

    def save(self, *args, **kwargs):
        max_extensions = self.get_max_extensions()

        if not self.pk:
            last_extension = RentalExtension.objects.filter(rental=self.rental).order_by("-extension_count").first()
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
