from django.db import models


class Course(models.Model):
    """
    Модель курса.
    """
    title = models.CharField(max_length=180, verbose_name="Название курса")
    preview = models.ImageField(upload_to="courses/previews", verbose_name="Превью", blank=True, null=True)
    description = models.TextField(verbose_name="Описание")

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self) -> str:
        return self.title


class Lesson(models.Model):
    """
    Модель урока, связанная с курсом.
    """
    title = models.CharField(max_length=180, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    preview = models.ImageField(upload_to="courses/previews", verbose_name="Превью", blank=True, null=True)
    video_url = models.URLField(verbose_name="Ссылка на видео")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons", verbose_name="Курс")

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self) -> str:
        return f"{self.title} ({self.course.title})"
