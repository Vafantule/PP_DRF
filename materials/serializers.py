from typing import Any, Dict, Optional

from rest_framework import serializers
from rest_framework.request import Request

from .models import Course, Lesson, Payment, Subscription
from .validators import VideoDomainValidator


class LessonSerializer(serializers.ModelSerializer):
    """
    Сериализатор урока.
    """
    owner = serializers.ReadOnlyField(source="owner.id")

    class Meta:
        model = Lesson
        fields = "__all__"
        read_only_fields = ["owner"]
        validators = [VideoDomainValidator(field="video_url")]


class CourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор курса.
    """
    lessons_count = serializers.SerializerMethodField(read_only=True)
    lessons = LessonSerializer(many=True, read_only=True)
    owner = serializers.ReadOnlyField(source="owner.id")

    class Meta:
        model = Course
        fields = "__all__"
        read_only_fields = ["owner", "lessons_count", "lessons"]

    def get_lessons_count(self, obj: Course) -> int:
        return obj.lessons.count()


class CourseSubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор курса на подписку.
    """
    user = serializers.ReadOnlyField(source="user.id")
    created_at = serializers.ReadOnlyField()

    class Meta:
        model = Subscription
        fields = ["id", "user", "course", "created_at"]
        read_onl_fields = ["id", "user", "created_at"]

    def create(self, validated_data: Dict[str, Any]) -> Subscription:
        request: Optional[Request] = self.context.get("request")
        if request is None or not getattr(request, "user", None):
            raise serializers.ValidationError("Не удалось получить текущего пользователя.")

        user = request.user
        course = validated_data["course"]
        subscription, _created = Subscription.objects.get_or_create(user=user, course=course)
        return subscription


class PaymentSerializer(serializers.ModelSerializer):
    """
    Сериализатор записи платежа.
    """
    class Meta:
        model = Payment
        fields = ["id", "user", "course", "amount", "currency", "stripe_session_url", "stripe_session_id"]
        read_only_fields = ["id", "user", "stripe_session_url", "stripe_session_id"]

    amount = serializers.IntegerField(min_value=1)
    currency = serializers.CharField(default="rub", required=False)

    def validate_course(self, value: Course) -> Course:
        if value is None:
            raise serializers.ValidationError("Неправильный курс")
        return value

    def create(self, validated_data: Dict[str, Any]) -> Payment:
        request = self.context.get("request")
        user = getattr(request, "user", None)
        validated_data["user"] = user
        payment = super().create(validated_data)
        return payment
