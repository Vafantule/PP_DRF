from typing import Any

from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, SerializerMethodField

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


class PaymentListSerializer(ModelSerializer):
    """
    Сериализатор для списка или истории платежей.
    """
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ["paid_at"]


class UserProfileSerializer(ModelSerializer):
    """
    Сериализатор профиля пользователя с историей платежей.
    """
    payments = PaymentListSerializer(many=True, read_only=True)
    payments_count = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = "__all__"
        read_only_fields = ["email", "payment_count", "payments"]

    def get_payments_count(self, obj: User) -> int:
        return obj.payments.count()
