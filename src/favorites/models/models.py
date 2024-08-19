from app.conf.auth import AUTH_USER_MODEL
from app.models import models
from books.models import Book


class FavoriteManager(models.Manager):
    """
    Менеджер для управления избранными книгами.

    Методы:
    - favorite_books_for_user: Возвращает избранные книги для указанного пользователя.
    - add_to_favorites: Добавляет книгу в избранное для указанного пользователя.
    - remove_from_favorites: Удаляет книгу из избранного для указанного пользователя.
    - is_favorite: Проверяет, является ли книга избранной для указанного пользователя.
    """

    def favorite_books_for_user(self, user):
        return self.filter(user=user).select_related('book')

    def add_to_favorites(self, user, book):
        if not self.filter(user=user, book=book).exists():
            self.create(user=user, book=book)

    def remove_from_favorites(self, user, book):
        self.filter(user=user, book=book).delete()

    def is_favorite(self, user, book):
        return self.filter(user=user, book=book).exists()


class Favorite(models.Model):
    """
    Модель для управления избранными книгами пользователя.

    Атрибуты:
    - user: Пользователь, который добавил книгу в избранное (ForeignKey).
    - book: Книга, добавленная в избранное (ForeignKey).
    - created_at: Дата и время добавления книги в избранное.

    Методы:
    - __str__: Возвращает строку с информацией о книге и пользователе.
    """

    user = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites'
    )
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"
