from typing import Any

from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class IsOwnerOrModeratorOrAdmin(BasePermission):
    """
    Класс разрешения для пользователей.
    """
    def _is_moderator(self, user: Any) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        try:
            return user.groups.filter(name="moderators").exists()
        except AttributeError:
            return False

    def has_permission(self, request: Request, view: APIView) -> bool:
        user = getattr(request, "user", None)
        if user is None or not getattr(user, "is_authenticated", False):
            return False

        if getattr(user, "is_superuser", False):
            return True

        is_moderator = self._is_moderator(user)

        if request.method in SAFE_METHODS or request.method in ("PUT", "PATCH"):
            return True

        if request.method == "POST" or request.method == "DELETE":
            return not is_moderator

        # if request.method == "DELETE":
        #     if is_moderator:
        #         return False
        #     return getattr(user, "is_staff", False) or getattr(user, "is_superuser", False)

        return False

    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        user = getattr(request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return False

        if getattr(user, "is_superuser", False):
            return True

        is_moderator = self._is_moderator(user)

        if request.method in SAFE_METHODS or request.method in ("PUT", "PATCH"):
            owner = getattr(obj, "owner", None)
            if owner is None:
                return False
            return is_moderator or owner == user

        if request.method == "DELETE":
            owner = getattr(obj, "owner", None)
            if owner is None:
                return False
            return owner == user

        return False
