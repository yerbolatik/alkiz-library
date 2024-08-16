from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as _UserManager

from app.models import models
from users.mixins import TimestampMixin


class User(TimestampMixin, AbstractUser):  # noqa
    objects: ClassVar[_UserManager] = _UserManager()

    telegram_id = models.CharField(max_length=100, unique=True)
    telegram_username = models.CharField(max_length=100, unique=True, null=True, blank=True)
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name", "phone_number"]

    def __str__(self):
        return self.username
