from django.db import transaction
from rest_framework import generics
from rest_framework.response import Response

from .mixins import CourseMixin
from .models import Course
from .permissions import IsStaffOrReadOnly
from .serializers import CourseDetailSerializer, CourseSummarySerializer


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
