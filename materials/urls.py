from django.urls import path
from rest_framework.routers import DefaultRouter

from .apps import MaterialsConfig
from .views import (CourseViewSet, LessonCreateAPIView, LessonDestroyAPIView, LessonListAPIView, LessonRetrieveAPIView,
                    LessonUpdateAPIView, CourseSubscriptionAPIView)

app_name = MaterialsConfig.name

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="courses")

urlpatterns = [
    path("lessons/", LessonListAPIView.as_view(), name="lessons_list"),
    path("lessons/create/", LessonCreateAPIView.as_view(), name="lesson_create"),
    path("lessons/<int:pk>/", LessonRetrieveAPIView.as_view(), name="lesson_retrieve"),
    path("lessons/<int:pk>/update/", LessonUpdateAPIView.as_view(), name="lesson_update"),
    path("lessons/<int:pk>/delete/", LessonDestroyAPIView.as_view(), name="lesson_delete"),
    path("courses/<int:course_id>/subscription/", CourseSubscriptionAPIView.as_view(), name="course-subscription")
] + router.urls
