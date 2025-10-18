from rest_framework import generics, viewsets, permissions
from rest_framework.permissions import AllowAny
from rest_framework.request import Request

from .models import Payment
from .serializers import UserRegistrationSerializer, PaymentSerializer


class UserRegistrationAPIView(generics.CreateAPIView):
    """
    Контроллер регистрации пользователя.
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class PaymentViewSet(viewsets.ModelViewSet):
    """
    Контроллер платежей, реализация через ViewSet.
    """
    queryset = Payment.objects.all().select_relater("user", "paid_course", "paid_lesson")
    serializer_class = PaymentSerializer

    def get_permissions(self) -> list[permissions.BasePermission]:
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer: PaymentSerializer) -> None:
        user = serializer.validated_data("user")
        if user is None and (isinstance(self.request, Request) and
                             self.request.user and
                             self.request.user.is_authenticated):
            serializer.save(user=self.request.user)
        else:
            serializer.save()
