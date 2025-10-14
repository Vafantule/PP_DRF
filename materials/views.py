from rest_framework import viewsets, generics

from materials.models import Course, Lesson
from materials.serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    Контроллер курса, реализация через ViewSet.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class LessonListAPIView(generics.ListAPIView):
    """
    Контроллер получения списка урока.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonCreateAPIView(generics.CreateAPIView):
    """
    Контроллер создания урока.
    """
    serializer_class = LessonSerializer


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """
    Контроллер получения одного урока.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonUpdateAPIView(generics.UpdateAPIView):
    """
    Контроллер изменения одного урока.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonDestroyAPIView(generics.DestroyAPIView):
    """
    Контроллер удаления одного урока.
    """
    queryset = Lesson.objects.all()
