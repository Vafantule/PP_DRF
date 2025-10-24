from django.db.models import QuerySet
from rest_framework import generics, viewsets

from materials.models import Course, Lesson
from materials.permissions import IsOwnerOrModeratorOrAdmin
from materials.serializers import CourseSerializer, LessonSerializer
from users.permissions import IsAdminOrModeratorEditOnly


class CourseViewSet(viewsets.ModelViewSet):
    """
    Контроллер курса, реализация через ViewSet.
    """
    queryset = Course.objects.all().prefetch_related("lessons")
    serializer_class = CourseSerializer
    permission_classes = [IsOwnerOrModeratorOrAdmin]

    def get_queryset(self) -> QuerySet[Course]:
        queryset = super().get_queryset()
        request = getattr(self, "request", None)
        if request is None:
            return queryset.none()
        user = request.user
        if getattr(user, "is_superuser", False) or user.groups.filter(name="moderators").exists():
            return queryset
        return queryset.filter(owner=user)

    def perform_create(self, serializer: CourseSerializer) -> None:
        request_user = getattr(self.request, "user", None)
        serializer.save(owner=request_user)


class LessonListAPIView(generics.ListAPIView):
    """
    Контроллер получения списка урока.
    """
    queryset = Lesson.objects.all().select_related("course")
    serializer_class = LessonSerializer
    permission_classes = [IsOwnerOrModeratorOrAdmin]

    def get_queryset(self) -> QuerySet[Lesson]:
        queryset = super().get_queryset()
        request = getattr(self, "request", None)
        if request is None:
            return queryset.none()
        user = request.user
        if getattr(user, "is_superuser", False) or user.groups.filter(name="moderators").exists():
            return queryset
        return queryset.filter(owner=user)

    def perform_create(self, serializer: LessonSerializer) -> None:
        request_user = getattr(self.request, "user", None)
        serializer.save(owner=request_user)


class LessonCreateAPIView(generics.CreateAPIView):
    """
    Контроллер создания урока.
    """
    serializer_class = LessonSerializer
    permission_classes = [IsOwnerOrModeratorOrAdmin]

    def perform_create(self, serializer: LessonSerializer) -> None:
        request_user = getattr(self.request, "user", None)
        serializer.save(owner=request_user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """
    Контроллер получения одного урока.
    """
    queryset = Lesson.objects.all().select_related("course")
    serializer_class = LessonSerializer
    permission_classes = [IsAdminOrModeratorEditOnly]


class LessonUpdateAPIView(generics.UpdateAPIView):
    """
    Контроллер изменения одного урока.
    """
    queryset = Lesson.objects.all().select_related("course")
    serializer_class = LessonSerializer
    permission_classes = [IsOwnerOrModeratorOrAdmin]


class LessonDestroyAPIView(generics.DestroyAPIView):
    """
    Контроллер удаления одного урока.
    """
    queryset = Lesson.objects.all().select_related("course")
    permission_classes = [IsOwnerOrModeratorOrAdmin]
