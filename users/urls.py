from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .apps import UsersConfig
from .views import PaymentViewSet, UserProfileViewSet, UserRegistrationAPIView, UserViewSet

app_name = UsersConfig.name

router = DefaultRouter()
router.register(r"payments", PaymentViewSet, basename="payments")
router.register(r"profiles", UserProfileViewSet, basename="user-profiles")
router.register(r"users", UserViewSet, basename="user")


urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='user-register'),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
] + router.urls
