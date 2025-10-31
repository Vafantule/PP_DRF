from typing import Optional, Dict, Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from .models import Course

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

        moderators_group = Group.objects.get_or_create(name="moderators")
        moderators_group.user_set.add(cls.moderator)

        cls.course_owner: Course = Course.objects.create(
            title="Владелец курса",
            description="Описание курса по владельцу",
            owner=cls.user_owner
        )

        cls.courses_list_url: str = "/materials/courses/"
        cls.course_detail_irl = lambda pk: f"/materials/course/{pk}"

    def setUp(self) -> None:
        self.client: APIClient= self.client

    def auth_as(self, user: Optional[User]) -> None:
        if user in None:
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

