from django.urls import path
from rest_framework.routers import DefaultRouter

from .apps import UsersConfig
from .views import PaymentViewSet, UserProfileViewSet, UserRegistrationAPIView

app_name = UsersConfig.name

router = DefaultRouter()
router.register(r"payments", PaymentViewSet, basename="payments")
router.register(r"profiles", UserProfileViewSet, basename="user-profiles")


urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='user-register'),
] + router.urls
