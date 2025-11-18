import logging
from datetime import timedelta
from typing import Any, Dict

from celery import shared_task
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, name="users.tasks.deactivate_inactive_users")
def deactivate_inactive_users(self, days: int = 30) -> Dict[str, Any]:
    """
    Функция деактивации неактивных (больше 30 дней) пользователей.
    """
    User = get_user_model()
    less_then_point = timezone.now() - timedelta(days=days)
    queryset = User.objects.filter(is_active=True, last_login__lt=less_then_point)
    total_candidates = queryset.count()

    with transaction.atomic():
        deactivated_count = queryset.update(is_active=False)

    logger.info(
        "deactivate_inactive_users: checked=%d, deactivated=%d, less_then_point=%s",
        total_candidates,
        deactivated_count,
        less_then_point.isoformat()
    )

    return {
        "status": "ok",
        "checked": total_candidates,
        "deactivated": deactivated_count,
        "less_then_point": less_then_point.isoformat()
    }
