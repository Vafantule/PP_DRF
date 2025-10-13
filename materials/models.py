from django.db import models


class Course(models.Model)
    """
    Модель курса.
    """
    title = models.CharField(max_length=180, verbose_name="Название курса")
    preview = models.ImageField(upload_to="courses/previews", verbose_name="Превью", blank=True, null=True)
    description = models.TextField(verbose_name="Описание")

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        return self.title
