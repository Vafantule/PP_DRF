from typing import Optional

from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response


class CourseLessonPagination(PageNumberPagination):
    """
    Пагинатор для списков курсов и уроков.
    """
    page_size: int = 10
    page_size_query_param: Optional[str] = "page_size"
    max_page_size: int = 100

    def get_paginated_response(self, data: Request) -> Response:
        return super().get_paginated_response(data)
