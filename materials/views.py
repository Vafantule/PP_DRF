from rest_framework import viewsets

from materials.models import Course
from materials.serializers import CourseSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    Контроллер курса, реализация через ViewSet.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
