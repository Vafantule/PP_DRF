from django.urls import path, include
from .apps import UsersConfig
from .views import UserRegistrationAPIView, PaymentViewSet
from rest_framework.routers import DefaultRouter


app_name = UsersConfig.name

router = DefaultRouter()
router.register(r"payments", PaymentViewSet, basename="payments")


urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='user-register'),
] + router.urls
