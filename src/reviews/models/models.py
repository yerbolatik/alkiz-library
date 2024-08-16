from app.conf.auth import AUTH_USER_MODEL
from app.models import models
from books.models import Book
from users.mixins import TimestampMixin


class Review(TimestampMixin, models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews")
    review_text = models.TextField()

    def __str__(self):
        return f"Review by {self.user.username} for {self.book.title}"


class Rating(TimestampMixin, models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ratings")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="ratings")
    score = models.IntegerField()

    def __str__(self):
        return f"Rating by {self.user.username} for {self.book.title}"
