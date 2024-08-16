from app.models import models
from users.mixins import TimestampMixin


class Category(TimestampMixin, models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Language(TimestampMixin, models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Author(TimestampMixin, models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    about = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to="author_photos/", blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Book(TimestampMixin, models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    authors = models.ManyToManyField("Author", related_name="books")
    publication_date = models.DateField()
    available = models.BooleanField(default=True)
    average_rating = models.FloatField(default=0.0)
    rating_count = models.PositiveIntegerField(default=0)
    rental_count = models.PositiveIntegerField(default=0)
    cover_image_url = models.ImageField(upload_to="book_covers/", blank=True, null=True)
    categories = models.ManyToManyField("Category", related_name="books", blank=True)
    language = models.ForeignKey("Language", null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
