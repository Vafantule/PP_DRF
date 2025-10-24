from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class IsAdminOrModeratorEditOnly(BasePermission):
    """
    Класс разрешения для moderators.
    """
    def _is_moderator(self, user: Any) -> bool:
        if not user or not user.is_authenticated:
            return False
        return user.groups.filter(name="moderators").exists()
