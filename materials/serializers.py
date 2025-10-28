from rest_framework import serializers

from .models import Course, Lesson
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
