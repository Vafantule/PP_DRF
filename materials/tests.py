from typing import Optional, Dict, Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.status import HTTP_201_CREATED
from rest_framework.test import APITestCase, APIClient

from .models import Course, Lesson

User = get_user_model()


class CourseAPITests(APITestCase):
    """
    Тесты для Course CRUD.
    """
    @classmethod
    def setUpTestData(cls) -> None:
        cls.superuser: User = User.objects.create_superuser(email="admin@example.com", password="adminpassword")
        cls.moderator: User = User.objects.create_user(email="moderator@example.com", password="moderatorpasword")
        cls.user_owner: User = User.objects.create_user(email="owner@example.com", password="ownerpassword")
        cls.user_other: User = User.objects.create_user(email="other@example.com", password="otherpassword")

        moderators_group, _ = Group.objects.get_or_create(name="moderators")
        moderators_group.user_set.add(cls.moderator)

        cls.course_owned: Course = Course.objects.create(
            title="Владелец курса",
            description="Описание курса по владельцу",
            owner=cls.user_owner
        )

        cls.courses_list_url: str = "/courses/"
        cls.course_detail_url = lambda pk: f"/courses/{pk}/"

    def setUp(self) -> None:
        self.client: APIClient= self.client

    def auth_as(self, user: Optional[User]) -> None:
        if user is None:
            self.client.force_authenticate(user=None)
        else:
            self.client.force_authenticate(user=user)

    def test_user_can_create_course_and_be_owner(self) -> None:
        self.auth_as(self.user_other)
        payload: Dict[str, Any] = {"title": "Новый курс", "description": "Описание"}
        response_custom = self.client.post(self.courses_list_url, payload, format="json")
        self.assertIn(response_custom.status_code, (status.HTTP_201_CREATED, status.HTTP_200_OK))
        if response_custom.status_code == status.HTTP_201_CREATED:
            data = response_custom.json()
            self.assertEqual(int(data.get("owner")), self.user_other.id)
            self.assertTrue(Course.objects.filter(pk=data.get("id"), owner=self.user_other).exists())

    def test_moderator_cannot_create_course(self) -> None:
        self.auth_as(self.moderator)
        payload = {"title": "Модератор курса", "description": "Запрещено"}
        response_custom = self.client.post(self.courses_list_url, payload, format="json")
        self.assertEqual(response_custom.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_can_create_course(self) -> None:
        self.auth_as(self.superuser)
        payload = {"title": "Администратор курса", "description": "Описание"}
        response_custom = self.client.post(self.courses_list_url, payload, format="json")
        self.assertEqual(response_custom.status_code, status.HTTP_201_CREATED)
        data = response_custom.json()
        self.assertEqual(int(data.get("owner")), self.superuser.id)

    def test_owner_can_update_own_course(self) -> None:
        self.auth_as(self.user_owner)
        response_custom = self.client.patch(self.course_detail_url(self.course_owned.id),
                                            {"title": "Обновлено"}, format="json")
        self.assertIn(response_custom.status_code, (status.HTTP_200_OK, status.HTTP_202_ACCEPTED))
        self.course_owned.refresh_from_db()
        self.assertEqual(self.course_owned.title, "Обновлено")

    def test_owner_can_delete_own_course(self) -> None:
        temp = Course.objects.create(title="Курс для теста", description="Тесты", owner=self.user_owner)
        self.auth_as(self.user_owner)
        response_custom = self.client.delete(self.course_detail_url(temp.id))
        self.assertIn(response_custom.status_code, (status.HTTP_204_NO_CONTENT, status.HTTP_200_OK))
        self.assertFalse(Course.objects.filter(pk=temp.id).exists())

    def test_moderator_cannot_delete_course(self) -> None:
        self.auth_as(self.moderator)
        response_custom = self.client.delete(self.course_detail_url(self.course_owned.id))
        self.assertEqual(response_custom.status_code, status.HTTP_403_FORBIDDEN)


class LessonAPITest(APITestCase):
    """
    Тесты для Lesson CRUD.
    """
    @classmethod
    def setUpTestData(cls) -> None:
        cls.superuser: User = User.objects.create_superuser(email="admin@example.com", password="adminpassword")
        cls.moderator: User = User.objects.create_user(email="moderator@example.com", password="moderatorpasword")
        cls.owner: User = User.objects.create_user(email="owner@example.com", password="ownerpassword")
        cls.other: User = User.objects.create_user(email="other@example.com", password="otherpassword")

        moderators_group, _ = Group.objects.get_or_create(name="moderators")
        moderators_group.user_set.add(cls.moderator)

        cls.course: Course = Course.objects.create(
            title="Курс",
            description="Описание курса",
            owner=cls.owner
        )
        cls.lesson_owned: Lesson = Lesson.objects.create(
            title="Владелец урока",
            description="Описание урока по владельцу",
            course=cls.course,
            owner=cls.owner,
            video_url="https://www.youtube.com/watch?v=qwerty321",
        )

        cls.lessons_list_url: str = reverse("materials:lessons_list")
        cls.lesson_create_url: str = reverse("materials:lesson_create")
        cls.lesson_detail_url = lambda pk: reverse("materials:lesson_retrieve", args=[pk])
        cls.lesson_update_url = lambda pk: reverse("materials:lesson_update", args=[pk])
        cls.lesson_delete_url = lambda pk: reverse("materials:lesson_delete", args=[pk])

    def setUp(self) -> None:
        self.client: APIClient= self.client

    def auth_as(self, user: Optional[User]) -> None:
        if user is None:
            self.client.force_authenticate(user=None)
        else:
            self.client.force_authenticate(user=user)

    def test_owner_can_create_lesson(self) -> None:
        self.auth_as(self.owner)
        payload: Dict[str, Any] = {
            "title": "Урок",
            "description": "Описание урока",
            "course": self.course.id,
            "video_url": "https://youtube.com/qwerty321",
        }
        response_custom = self.client.post(self.lesson_create_url, payload, format="json")
        self.assertIn(response_custom.status_code, (status.HTTP_201_CREATED, status.HTTP_200_OK))
        if response_custom.status_code == status.HTTP_201_CREATED:
            data = response_custom.json()
            self.assertEqual(int(data.get("owner")), self.owner.id)
            self.assertTrue(Lesson.objects.filter(pk=data.get("id"), owner=self.owner). exists())

    def test_moderator_cannot_create_lesson(self) -> None:
        self.auth_as(self.moderator)
        payload = {
            "title": "Модератор урока",
            "description": "Запрещено",
            "course": self.course.id,
            "video_url": "https://www.youtube.com/watch?v=mod123",
        }
        response_custom = self.client.post(self.lesson_create_url, payload, format="json")
        self.assertEqual(response_custom.status_code, status.HTTP_403_FORBIDDEN)

    def test_any_authenticated_can_retrieve_lesson_detail(self) -> None:
        self.auth_as(self.other)
        response_custom = self.client.get(self.lesson_detail_url(self.lesson_owned.id))
        self.assertEqual(response_custom.status_code, status.HTTP_200_OK)
        data = response_custom.json()
        self.assertEqual(data.get("id"), self.lesson_owned.id)

    def test_owner_can_update_own_lesson(self) -> None:
        self.auth_as(self.owner)
        response_custom = self.client.patch(self.lesson_update_url(self.lesson_owned.id),{"title": "Обновлено"})
        self.assertIn(response_custom.status_code, (status.HTTP_200_OK, status.HTTP_202_ACCEPTED))
        self.lesson_owned.refresh_from_db()
        self.assertEqual(self.lesson_owned.title, "Обновлено")

    def test_other_cannot_update_not_owned_lesson(self) -> None:
        self.auth_as(self.other)
        response_custom = self.client.patch(self.lesson_update_url(self.lesson_owned.id), {"title": "Название"})
        self.assertEqual(response_custom.status_code, status.HTTP_403_FORBIDDEN)
