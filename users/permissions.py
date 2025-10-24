from typing import Any

from rest_framework.permissions import BasePermission, SAFE_METHODS
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

    def has_permission(self, request: Request, view: APIView) -> bool:
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False

        if getattr(user, "is_superuser", False):
            return True

        is_moderator = self._is_moderator(user)

        if request.method in SAFE_METHODS:
            return True
