from django.urls import path

from .apps import MaterialsConfig
from .views import (CourseViewSet,
                    LessonListView, LessonCreateView, LessonRetrieveView, LessonUpdateView, LessonDestroyView)
from rest_framework.routers import DefaultRouter


app_name = MaterialsConfig.name

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="courses")

urlpatterns = [
    path("lessons/", LessonListView.as_view(), name="lessons_list"),
    path("lessons/create/", LessonCreateView.as_view(), name="lesson_create"),
    path("lessons/<int:pk>/", LessonRetrieveView.as_view(), name="lesson_retrieve"),
    path("lessons/<int:pk>/update/", LessonUpdateView.as_view(), name="lesson_update"),
    path("lessons/<int:pk>/delete/", LessonDestroyView.as_view(), name="lesson_delete"),
] + router.urls
