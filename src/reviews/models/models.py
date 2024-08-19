from app.conf.auth import AUTH_USER_MODEL
from app.models import models
from books.models import Book
from users.mixins import TimestampMixin


class ReviewManager(models.Manager):
    """
    Менеджер для управления рецензиями на книги.

    Методы:
    - reviews_for_book: Возвращает рецензии для указанной книги.
    - reviews_by_user: Возвращает рецензии, написанные указанным пользователем.
    """

    def reviews_for_book(self, book):
        return self.filter(book=book)

    def reviews_by_user(self, user):
        return self.filter(user=user)


class Review(TimestampMixin, models.Model):
    """
    Рецензия на книгу.

    Атрибуты:
    - user: Пользователь, написавший рецензию (ForeignKey).
    - book: Книга, на которую написана рецензия (ForeignKey).
    - review_text: Текст рецензии.

    Методы:
    - __str__: Возвращает строку с рецензией пользователя для книги.
    """

    user = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="reviews")
    review_text = models.TextField()

    objects = ReviewManager()

    def __str__(self):
        return f"Review by {self.user.username} for {self.book.title}"


class RatingManager(models.Manager):
    """
    Менеджер для управления рейтингами книг.

    Методы:
    - rating_for_book: Возвращает рейтинги для указанной книги.
    - average_rating_for_book: Возвращает средний рейтинг для указанной книги.
    """

    def rating_for_book(self, book):
        return self.filter(book=book)

    def average_rating_for_book(self, book):
        return self.filter(book=book).aaggregate(models.Avg('score'))['score__avg']


class Rating(TimestampMixin, models.Model):
    """
    Рейтинг книги.

    Атрибуты:
    - user: Пользователь, оставивший рейтинг (ForeignKey).
    - book: Книга, которая оценивается (ForeignKey).
    - score: Оценка книги (целое число).

    Методы:
    - __str__: Возвращает строку с рейтингом пользователя для книги.
    """

    user = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ratings")
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="ratings")
    score = models.IntegerField()

    objects = RatingManager()

    def __str__(self):
        return f"Rating by {self.user.username} for {self.book.title}"
