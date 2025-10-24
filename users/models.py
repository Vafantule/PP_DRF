from decimal import Decimal
from typing import Any

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Менеджер для кастомной модели User.
    """
    use_in_migrations = True

    def create_user(self, email: str, password: str, **extra_fields: Any) -> "User":
        if not email:
            raise ValueError("Email должен быть задан.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str, **extra_fields: Any) -> "User":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен быть is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен быть is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


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
    REQUIRED_FIELDS: list[str] = []

    objects = CustomUserManager()

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
        (METHOD_CASH, "Наличные"),
        (METHOD_TRANSFER, "Перевод на счет"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name="payments",
                             verbose_name="Пользователь")
    paid_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата оплаты")
    paid_course = models.ForeignKey("materials.Course",
                                    on_delete=models.SET_NULL,
                                    related_name="payments",
                                    verbose_name="Оплаченный курс",
                                    blank=True, null=True)
    paid_lesson = models.ForeignKey("materials.Lesson",
                                    on_delete=models.SET_NULL,
                                    related_name="payments",
                                    verbose_name="Оплаченный урок",
                                    blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма оплаты", default=Decimal("0.00"))
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, verbose_name="Способ оплаты")

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ["-paid_at"]

    def __str__(self) -> str:
        target = self.paid_course or self.paid_lesson
        target_representative = getattr(target, "title", str(target)) if target else "—"
        return f"Платеж №{self.pk} по {self.user} для {target_representative} ({self.amount})"

    def clean(self) -> None:
        """
        Проверка целостности платежа.
        """
        errors: dict[str, str] = {}
        if self.paid_course and self.paid_lesson:
            errors["paid_course"] = "Укажите либо оплаченный курс, либо оплаченный урок."
            errors["paid_lesson"] = "Укажите либо оплаченный урок, либо оплаченный курс."
        if not self.paid_course and not self.paid_lesson:
            errors["paid_course"] = "Необходимо указать оплаченный урок либо курс."
        if self.amount is None or self.amount < 0:
            errors["amount"] = "Сумма оплаты должна быть больше 0."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)
