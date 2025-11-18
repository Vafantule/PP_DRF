from django.conf import settings
from django.db import models
from django.utils import timezone


class Course(models.Model):
    """
    Модель курса.
    """
    title = models.CharField(max_length=180, verbose_name="Название курса")
    preview = models.ImageField(upload_to="courses/previews", verbose_name="Превью", blank=True, null=True)
    description = models.TextField(verbose_name="Описание")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses",
        verbose_name="Владелец",
        null=True,
        blank=True,
    )
    update_at = models.DateTimeField(auto_now=True)
    last_notification_sent = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self) -> str:
        return self.title

    def should_notify_now(self, interval_hours: int = 4) -> bool:
        if self.last_notification_sent is None:
            return True
        time_delta = timezone.now() - self.last_notification_sent
        return time_delta.total_seconds() >= interval_hours * 3600


class Lesson(models.Model):
    """
    Модель урока, связанная с курсом.
    """
    title = models.CharField(max_length=180, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    preview = models.ImageField(upload_to="courses/previews", verbose_name="Превью", blank=True, null=True)
    video_url = models.URLField(verbose_name="Ссылка на видео")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons", verbose_name="Курс")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Владелец",
        null=True,
        blank=True,
    )
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self) -> str:
        return f"{self.title} ({self.course.title})"


class Subscription(models.Model):
    """
    Модель пользователя на обновления курса.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_subscriptions",
        verbose_name="Пользователь",
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="subscriptions", verbose_name="Курс")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата подписки")

    class Meta:
        verbose_name = "Подписка на курс"
        verbose_name_plural = "Подписки на курс"
        constraints = [models.UniqueConstraint(fields=["user", "course"], name="unique_user_course_subscription")]

    def __str__(self):
        return f"Подписка (пользователь={self.user_id}, курс={self.course_id})"


class Payment(models.Model):
    """
    Модель платежа.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="платежи")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="платежи")
    amount = models.PositiveIntegerField(help_text="Сумма в рублях")
    currency = models.CharField(max_length=10, default="rub")
    stripe_product_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_price_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_session_url = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=32, default="создан")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

    def __str__(self) -> str:
        return f"Платеж (номер={self.pk}, пользователь={self.user_id}, курс={self.course_id}, сумма={self.amount})"
