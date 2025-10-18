from typing import Any

from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from .models import Payment

User = get_user_model()


class UserRegistrationSerializer(ModelSerializer):
    """
    Сериализатор для регистрации пользователя.
    """
    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            phone=validated_data.get("phone", ""),
            city=validated_data.get("city", ""),
            avatar=validated_data.get("avatar", None),
        )
        return user


class PaymentSerializer(ModelSerializer):
    """
    Сериализатор для платежей.
    """
    class Meta:
        model = Payment
        fields = ["id", "user", "paid_at", "paid_course", "paid_lesson", "amount", "method"]
        read_only_fields = ["paid_at"]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        paid_course = attrs.get("paid_course")
        paid_lesson = attrs.get("paid_lesson")
        amount = attrs.get("amount")

        if paid_course and paid_lesson:
            raise ValidationError("Укажите либо оплаченный курс, либо оплаченный урок.")
        if not paid_course and not paid_lesson:
            raise ValidationError("Необходимо указать оплаченный урок либо курс.")
        if amount is None or amount < 0:
            raise ValidationError("Сумма оплаты должна быть больше 0.")
        return attrs
