from typing import Any, Dict, List

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from .models import Course, Subscription


@shared_task(bind=True, name="materials.tasks.send_course_update_notifications")
def send_course_update_notifications(self, course_id: int, update_summary: str) -> Dict[str, Any]:
    """
    Функция отправки писем подписчикам курса.
    """
    try:
        course: Course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return {
            "status": "course_not_found",
            "course_id": course_id,
        }

    subscriber_queryset = Subscription.objects.filter(course=course).select_related("user")
    emails: List[str] = [subscriber.user.email for subscriber in subscriber_queryset if
                         subscriber.user and subscriber.user.email]

    if not emails:
        return {
            "status": "no_subscribers",
            "count": 0,
            "course_id": course_id,
        }

    subject: str = f"Обновление курса: {course.title}."
    message: str = (f"Курс '{course.title}' обновлён.\n\nИзменения:\n{update_summary}\n\n"
                    f"Перейдите в приложение для просмотра обновлений.")
    from_email: str = getattr(settings, "DEFAULT_FROM_EMAIL", "example@example.com")

    sent_count: int = 0
    for email in emails:
        try:
            send_mail(subject, message, from_email, [email], fail_silently=False)
            sent_count += 1
        except Exception as exception:
            self.update_state(state="FAILURE", meta={"error": str(exception), "email": email})
            continue

    with transaction.atomic():
        course.last_notification_sent = timezone.now()
        course.save(update_fields=["last_notification_sent"])

    return {
        "status": "ok",
        "sent": sent_count,
        "total": len(emails),
        "course_id": course_id,
    }
