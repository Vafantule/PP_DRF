from decimal import Decimal
from typing import Optional

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from materials.models import Lesson, Course
from users.models import Payment

User = get_user_model()


class Command(BaseCommand):
    """
    Команда для создания записей в таблице payments.
    """
    def handle(self, *args, **options) -> None:
        user: Optional[User] = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR("Создайте пользователя."))
            return

        course: Optional[Course] = Course.objects.first()

        created_count = 0

        if course:
            payment_1 = Payment.objects.create(
                user=user,
                paid_course=course,
                amount=Decimal('499.99'),
                method=Payment.METHOD_TRANSFER,
            )
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f"По курсу {course.title} создан платеж: {payment_1}"))
        else:
            self.stdout.write(self.style.WARNING(f"Курс не найден; платеж за курс не создан."))

        lesson: Optional[Lesson] = Lesson.objects.first()

        if lesson:
            payment_2 = Payment.objects.create(
                user=user,
                paid_lesson=lesson,
                amount=Decimal('999.99'),
                method=Payment.METHOD_CASH,
            )
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f"По уроку {lesson.title} создан платеж: {payment_2}"))
        else:
            self.stdout.write(self.style.WARNING(f"Урок не найден; платеж за урок не создан."))

        if created_count:
            self.stdout.write(self.style.SUCCESS(f"{created_count} платежей создано."))
        else:
            self.stdout.write(self.style.ERROR(f"Ни одного платежа не создано."))
