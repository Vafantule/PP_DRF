from rest_framework import generics, viewsets, permissions
from rest_framework.permissions import AllowAny

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
