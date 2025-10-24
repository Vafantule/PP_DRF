from rest_framework import generics, viewsets

from materials.models import Course, Lesson
from materials.serializers import CourseSerializer, LessonSerializer
from users.permissions import IsAdminOrModeratorEditOnly


class CourseViewSet(viewsets.ModelViewSet):
    """
    Контроллер курса, реализация через ViewSet.
    """
    queryset = Course.objects.all().prefetch_related("lessons")
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrModeratorEditOnly]


class LessonListAPIView(generics.ListAPIView):
    """
    Контроллер получения списка урока.
    """
    queryset = Lesson.objects.all().select_related("course")
    serializer_class = LessonSerializer
    permission_classes = [IsAdminOrModeratorEditOnly]


class LessonCreateAPIView(generics.CreateAPIView):
    """
    Контроллер создания урока.
    """
    serializer_class = LessonSerializer
    permission_classes = [IsAdminOrModeratorEditOnly]


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
    permission_classes = [IsAdminOrModeratorEditOnly]


class LessonDestroyAPIView(generics.DestroyAPIView):
    """
    Контроллер удаления одного урока.
    """
    queryset = Lesson.objects.all().select_related("course")
    permission_classes = [IsAdminOrModeratorEditOnly]
