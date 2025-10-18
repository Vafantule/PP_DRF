from decimal import Decimal

from django.conf import settings
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


class Payment(models.Model):
    """
    Модель пользователя.
    """
    METHOD_CASH = "cash"
    METHOD_TRANSFER = "transfer"
    METHOD_CHOICES = [
        METHOD_CASH, "Наличные",
        METHOD_TRANSFER, "Перевод на счет",
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name="payments",
                             verbose_name='Пользователь')
    paid_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата оплаты")
    paid_course = models.ForeignKey("materials.Course",
                                    on_delete=models.SET_NULL,
                                    related_name="payments",
                                    verbose_name="Оплаченный курс",
                                    blank=True,
                                    null=True)
    paid_lesson = models.ForeignKey("materials.Lesson",
                                    on_delete=models.SET_NULL,
                                    related_name="payments",
                                    verbose_name="Оплаченный урок",
                                    blank=True,
                                    null=True)
    amount = models.DecimalField(max_length=10, decimal_places=2, verbose_name="Сумма оплаты", default=Decimal("0.00"))
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, verbose_name="Способ оплаты")

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ["-paid_at"]
