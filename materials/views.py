from rest_framework import viewsets, generics

from materials.models import Course, Lesson
from materials.serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    Контроллер курса, реализация через ViewSet.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class LessonListView(generics.ListAPIView):
    """
    Контроллер получения списка урока.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonCreateView(generics.CreateAPIView):
    """
    Контроллер создания урока.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonRetrieveView(generics.RetrieveAPIView):
    """
    Контроллер получения одного урока.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonUpdateView(generics.UpdateAPIView):
    """
    Контроллер изменения одного урока.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
