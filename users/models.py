from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Модель пользователя.
    """
    username = None

    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=16, verbose_name="Телефон", blank=True)
    city = models.CharField(max_length=99, verbose_name="Город", blank=True)
    avatar = models.ImageField(upload_to="users/avatars/", verbose_name="Аватар", blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
