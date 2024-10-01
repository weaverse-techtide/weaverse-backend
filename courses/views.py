from django.db import transaction
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.response import Response

from .mixins import CourseMixin
from .models import Course
from .permissions import IsStaffOrReadOnly
from .serializers import CourseDetailSerializer, CourseSummarySerializer


@extend_schema_view(
    get=extend_schema(
        summary="Course를 조회하는 API",
        description="특정 Course를 조회합니다. 누구나 조회할 수 있습니다.",
        responses={200: CourseDetailSerializer},
    ),
    put=extend_schema(
        summary="Course를 수정하는 API",
        description="특정 Course를 수정합니다. staff만 수정할 수 있습니다.",
        request=CourseDetailSerializer,
        responses={200: CourseDetailSerializer},
    ),
    patch=extend_schema(
        summary="Course를 부분 수정하는 API",
        description="특정 Course를 부분 수정합니다. staff만 수정할 수 있습니다.",
        request=CourseDetailSerializer,
        responses={200: CourseDetailSerializer},
    ),
    delete=extend_schema(
        summary="Course를 삭제하는 API",
        description="특정 Course를 삭제합니다. staff만 삭제할 수 있습니다.",
        responses={204: None},
    ),
)
class CourseDetailRetrieveUpdateDestroyView(
    CourseMixin, generics.RetrieveUpdateDestroyAPIView
):
    """
    course를 조회하거나 수정하거나 삭제합니다.
    """

    queryset = Course.objects.prefetch_related(
        "lectures__topics__multiple_choice_question__multiple_choice_question_choices",
        "lectures__topics__assignment",
    )
    serializer_class = CourseDetailSerializer
    permission_classes = [IsStaffOrReadOnly]

    def get_permissions(self):
        """
        GET 요청에만 대해서는 권한을 체크하지 않습니다.
        기본적으로 IsStaffOrReadOnly 권한이 필요합니다.
        """

        if self.request.method == "GET":
            return []
        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        """
        course를 수정합니다.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = self.get_object()
        self.perform_update(serializer, course)
        if getattr(course, "_prefetched_objects_cache", None):
            course._prefetched_objects_cache = {}
        serializer = self.get_serializer(course)
        return Response(serializer.data)

    @transaction.atomic
    def perform_update(self, serializer, course):
        """
        course 및 하위 모델 lecture, topic, assignment, quiz 등을 함께 수정합니다.
        """

        self.update_course_with_lectures_and_topics(
            course, serializer.data, serializer.data.get("lectures", [])
        )


@extend_schema_view(
    get=extend_schema(
        summary="Course 목록을 조회하는 API",
        description="Course 목록을 조회합니다. 누구나 조회할 수 있습니다.",
        responses={200: CourseSummarySerializer},
    ),
    post=extend_schema(
        summary="Course를 생성하는 API",
        description="Course를 생성합니다. staff만 생성할 수 있습니다.",
        request=CourseDetailSerializer,
        responses={201: CourseDetailSerializer},
    ),
)
class CourseListCreateView(CourseMixin, generics.ListCreateAPIView):
    """
    course 목록을 조회하거나 새로운 course를 생성합니다.
    """

    queryset = Course.objects.all()
    permission_classes = [IsStaffOrReadOnly]

    def get_serializer_class(self):
        """
        요청 메서드에 따라 다른 serializer를 반환합니다.

        - POST: CourseDetailSerializer
        - 그 외: CourseSummarySerializer
        """

        if self.request.method == "POST":
            return CourseDetailSerializer
        return CourseSummarySerializer

    @transaction.atomic
    def perform_create(self, serializer):
        """
        course 및 하위 모델 lecture, topic, assignment, quiz 등을 함께 생성합니다.
        """

        self.create_course_with_lectures_and_topics(
            serializer.data, serializer.data.get("lectures", [])
        )
