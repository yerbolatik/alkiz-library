from django.db.models import Q

from app.models import models
from users.mixins import TimestampMixin


class Category(TimestampMixin, models.Model):
    """
    Категория книги.

    Атрибуты:
    - name: Название категории (уникально).
    - description: Описание категории (необязательно).

    Методы:
    - __str__: Возвращает название категории в виде строки.
    """

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Language(TimestampMixin, models.Model):
    """
    Язык книги.

    Атрибуты:
    - name: Название языка (уникально).

    Методы:
    - __str__: Возвращает название языка в виде строки.
    """

    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Author(TimestampMixin, models.Model):
    """
    Автор книги.

    Атрибуты:
    - first_name: Имя автора.
    - last_name: Фамилия автора.
    - about: Информация об авторе (необязательно).
    - photo: Фотография автора (необязательно).

    Методы:
    - __str__: Возвращает полное имя автора в виде строки.
    """

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    about = models.TextField(blank=True, null=True)
    photo = models.ImageField(
        upload_to="author_photos/", blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class BookManager(models.Manager):
    """
    Менеджер для управления книгами.

    Методы:
    - available_book: Возвращает доступные книги.
    - books_by_category: Возвращает книги по названию категории.
    - book_by_author: Возвращает книги по имени и/или фамилии автора.
    - books_by_language: Возвращает книги по названию языка.
    """

    def available_book(self):
        return self.filter(available=True)

    def books_by_category(self, category_name):
        return self.filter(categories__name=category_name)

    def book_by_author(self, first_name=None, last_name=None):
        filters = Q()

        if first_name:
            filters &= Q(authors__first_name__iexact=first_name)
        if last_name:
            filters &= Q(authors__last_name__iexact=last_name)

        return self.filter(filters).distinct()

    def books_by_language(self, language_name):
        return self.filter(language__name__iexact=language_name)


class Book(TimestampMixin, models.Model):
    """
    Книга.

    Атрибуты:
    - title: Заголовок книги.
    - description: Описание книги (необязательно).
    - authors: Список авторов книги (ManyToMany).
    - publication_date: Дата публикации книги.
    - available: Статус доступности книги.
    - average_rating: Средний рейтинг книги.
    - rating_count: Количество оценок книги.
    - rental_count: Количество аренд книги.
    - cover_image: Обложки книги (необязательно).
    - categories: Категории книги (ManyToMany).
    - language: Язык книги (ForeignKey).

    Методы:
    - __str__: Возвращает заголовок книги в виде строки.
    """

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    authors = models.ManyToManyField("Author", related_name="books")
    publication_date = models.DateField()
    available = models.BooleanField(default=True)
    average_rating = models.FloatField(default=0.0)
    rating_count = models.PositiveIntegerField(default=0)
    rental_count = models.PositiveIntegerField(default=0)
    cover_image = models.ImageField(
        upload_to="book_covers/", blank=True, null=True)
    categories = models.ManyToManyField(
        "Category", related_name="books", blank=True)
    language = models.ForeignKey(
        "Language", null=True, on_delete=models.CASCADE)

    objects = BookManager()

    def __str__(self):
        return self.title
