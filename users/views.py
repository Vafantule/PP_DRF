from typing import List

from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.request import Request

from .models import Payment
from .serializers import PaymentSerializer, UserProfileSerializer, UserRegistrationSerializer, UserSerializer

User = get_user_model()


class UserRegistrationAPIView(generics.CreateAPIView):
    """
    Контроллер регистрации пользователя.
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    """
    Контроллер для авторизированных пользователей.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self) -> List[permissions.BasePermission]:
        return [permissions.IsAuthenticated()]


class PaymentViewSet(viewsets.ModelViewSet):
    """
    Контроллер платежей, реализация через ViewSet.
    """
    queryset = Payment.objects.all().select_related("user", "paid_course", "paid_lesson")
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends: List = [OrderingFilter, DjangoFilterBackend]
    filterset_fields = ["paid_course", "paid_lesson", "method"]
    ordering_fields = ["paid_at"]
    ordering = ["-paid_at"]

    def get_permissions(self) -> list[permissions.BasePermission]:
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer: PaymentSerializer) -> None:
        user = serializer.validated_data.get("user")
        if user is None and (isinstance(self.request, Request)
                             and self.request.user
                             and self.request.user.is_authenticated):
            serializer.save(user=self.request.user)
        else:
            serializer.save()


class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Контроллер для отображения профилей пользователей с историей платежей.
    """
    queryset = User.objects.all().prefetch_related("payments")
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.AllowAny]
