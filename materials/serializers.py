from typing import Dict, Any, Optional

from rest_framework import serializers
from rest_framework.request import Request

from .models import Course, Lesson, Subscription
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
    created_at =serializers.ReadOnlyField()

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
