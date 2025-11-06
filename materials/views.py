from typing import Dict, Any

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Course, Lesson, Subscription, Payment
from .serializers import CourseSerializer, LessonSerializer, CourseSubscriptionSerializer, PaymentSerializer
from .pagination import CourseLessonPagination
from users.permissions import IsOwnerOrModeratorOrAdmin
from .services import create_product, create_price, create_checkout_session, retrieve_session


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


class PaymentCreateAPIView(generics.CreateAPIView):
    """
    Контроллер создания платежа.
    """
    serializer_class = PaymentSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer: PaymentSerializer) -> None:
        payment: Payment = serializer.save()
        course = payment.course

        product_response = create_product(name=course.title, description=course.description)
        product_id = product_response.get("id")
        price_response = create_price(product_id=product_id, unit_amount=payment.amount, currency=payment.currency)
        price_id = price_response.get("id")

        success_url = self.request.build_absolute_uri("/")
        cancel_url = self.request.build_absolute_uri("/")
        session_response = create_checkout_session(
            price_id=price_id,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"payment_id": str(payment.id)}
        )
        session_id = session_response.get("id")
        session_url = session_response.get("url")

        payment.stripe_product_id = product_id
        payment.stripe_price_id = price_id
        payment.stripe_session_id = session_id
        payment.stripe_session_url = session_url
        payment.status = session_response.get("payment_status", payment.status) or payment.status
        payment.save()

        self._stripe_result: Dict[str, Any] = {
            "stripe_product": product_response,
            "stripe_price": price_response,
            "stripe_session": session_response,
        }

    def create(self, request, *args: Any, **kwargs: Any) -> Response:
        response = super().create(request, *args, **kwargs)
        payment = Payment.objects.get(pk=response.data["id"])
        extra_data = {
            "stripe_session_url": payment.stripe_session_url,
            "stripe_session_id": payment.stripe_session_id,
            "stripe_product_id": payment.stripe_product_id,
            "stripe_price_id": payment.stripe_price_id,
            "status": payment.status,
        }
        combined_data = {**response.data, **extra_data}
        return Response(combined_data, status=status.HTTP_201_CREATED)


class PaymentSessionStatusAPIView(generics.GenericAPIView):
    """
    Контроллер получения статуса сессии по id.
    """
    permission_classes = [AllowAny]

    def get(self, session_id: str) -> Response:
        session = retrieve_session(session_id=session_id)
        return Response(session, status=status.HTTP_200_OK)
