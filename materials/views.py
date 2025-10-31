from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Course, Lesson, Subscription
from .serializers import CourseSerializer, LessonSerializer, CourseSubscriptionSerializer
from .pagination import CourseLessonPagination
from users.permissions import IsOwnerOrModeratorOrAdmin


class CourseViewSet(viewsets.ModelViewSet):
    """
    Контроллер курса, реализация через ViewSet.
    """
    queryset = Course.objects.all().prefetch_related("lessons")
    serializer_class = CourseSerializer
    permission_classes = [IsOwnerOrModeratorOrAdmin]
    pagination_class = CourseLessonPagination

    def get_queryset(self) -> QuerySet[Course]:
        queryset_custom = super().get_queryset()
        request = getattr(self, "request", None)
        if request is None:
            return queryset_custom.none()
        user = request.user
        if getattr(user, "is_superuser", False) or user.groups.filter(name="moderators").exists():
            return queryset_custom
        return queryset_custom.filter(owner=user)

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
    pagination_class = CourseLessonPagination

    def get_queryset(self) -> QuerySet[Lesson]:
        queryset_custom = super().get_queryset()
        request = getattr(self, "request", None)
        if request is None:
            return queryset_custom.none()
        user = request.user
        if getattr(user, "is_superuser", False) or user.groups.filter(name="moderators").exists():
            return queryset_custom
        return queryset_custom.filter(owner=user)

    def perform_create(self, serializer: LessonSerializer) -> None:
        request_user = getattr(self.request, "user", None)
        serializer.save(owner=request_user)


class LessonCreateAPIView(generics.CreateAPIView):
    """
    Контроллер создания урока.
    """
    serializer_class = LessonSerializer
    permission_classes = [IsOwnerOrModeratorOrAdmin]
    pagination_class = CourseLessonPagination

    def perform_create(self, serializer: LessonSerializer) -> None:
        request_user = getattr(self.request, "user", None)
        serializer.save(owner=request_user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """
    Контроллер получения одного урока.
    """
    queryset = Lesson.objects.all().select_related("course")
    serializer_class = LessonSerializer
    permission_classes = [IsOwnerOrModeratorOrAdmin]


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


class CourseSubscriptionAPIView(APIView):
    """
    Контроллер APIView для подписки/отписки пользователя на курс.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, course_id: int) -> Response:
        course = get_object_or_404(Course, pk=course_id)
        subscription, created =Subscription.objects.get_or_create(user=request.user, course=course)
        serializer = CourseSubscriptionSerializer(subscription, context={"request": request})
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=status_code)

    def delete(self, request: Request, course_id: int) -> Response:
        course = get_object_or_404(Course, pk=course_id)
        deleted_count, _details = Subscription.objects.filter(user=request.user, course=course).delete()
        if deleted_count:
            return Response({"detail": "Подписка удалена."}, status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Подписки не было."}, status=status.HTTP_200_OK)
