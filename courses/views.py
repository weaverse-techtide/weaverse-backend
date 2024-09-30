from django.db import transaction
from rest_framework import generics
from rest_framework.response import Response

from .models import (
    Assignment,
    Course,
    Lecture,
    MultipleChoiceQuestion,
    MultipleChoiceQuestionChoice,
    Topic,
)
from .permissions import IsStaffOrReadOnly
from .serializers import CourseDetailSerializer, CourseSummarySerializer


class CourseDetailRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
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
            # 만약 'prefetch_related'가 queryset에 적용되었다면, instance의 prefetch cache를 강제로 무효화합니다.
            # 이는 수정된 데이터를 반영하기 위함입니다.
            course._prefetched_objects_cache = {}
        serializer = self.get_serializer(course)
        return Response(serializer.data)

    @transaction.atomic
    def perform_update(self, serializer, course):
        """
        course 및 하위 모델 lecture, topic, assignment, quiz 등을 함께 수정합니다.
        """
        course.title = serializer.data.get("title")
        course.short_description = serializer.data.get("short_description")
        course.description = serializer.data.get("description")
        course.category = serializer.data.get("category")
        course.course_level = serializer.data.get("course_level")
        course.save()

        course.lectures.all().delete()
        if serializer.data.get("lectures") is None:
            return
        for lecture_data in serializer.data.get("lectures"):
            lecture = self.create_lecture(lecture_data, course)
            if lecture_data.get("topics") is None:
                continue
            for topic_data in lecture_data.get("topics"):
                topic = self.create_topic(topic_data, lecture)
                self.handle_topic_type(topic, topic_data)

    def create_lecture(self, lecture_data, course):
        """
        lecture를 생성하고 반환합니다.

        params:
            course: Course
            lecture_data: dict
            - title: str
            - order: int
        """
        return Lecture.objects.create(
            course=course,
            title=lecture_data.get("title"),
            order=lecture_data.get("order"),
        )

    def create_topic(self, topic_data, lecture):
        """
        topic을 생성하고 반환합니다.

        params:
            lecture: Lecture
            topic_data: dict
            - title: str
            - type: str
            - description: str
            - order: int
            - is_premium: bool
        """
        return Topic.objects.create(
            lecture=lecture,
            title=topic_data.get("title"),
            type=topic_data.get("type"),
            description=topic_data.get("description"),
            order=topic_data.get("order"),
            is_premium=topic_data.get("is_premium"),
        )

    def handle_topic_type(self, topic, topic_data):
        """
        topic의 type에 따라 assignment 또는 quiz를 생성합니다.

        params:
            topic: Topic
            topic_data: dict
            - type: str
            - assignment: dict (optional)
            - multiple_choice_question: dict (optional)
        """
        if topic_data.get("type") == "assignment":
            self.create_assignment(topic, topic_data.get("assignment"))
        elif topic_data.get("type") == "quiz":
            self.create_quiz(topic, topic_data.get("multiple_choice_question"))

    def create_assignment(self, topic, assignment_data):
        """
        assignment를 생성하고 반환합니다.

        params:
            topic: Topic
            assignment_data: dict
            - question: str
        """
        return Assignment.objects.create(
            topic=topic, question=assignment_data.get("question")
        )

    def create_quiz(self, topic, multiple_choice_question_data):
        """
        quiz를 생성하고 반환합니다.

        params:
            topic: Topic
            multiple_choice_question_data: dict
            - question: str
            - multiple_choice_question_choices: list
        """
        multiple_choice_question = MultipleChoiceQuestion.objects.create(
            topic=topic,
            question=multiple_choice_question_data.get("question"),
        )
        for choice_data in multiple_choice_question_data.get(
            "multiple_choice_question_choices"
        ):
            self.create_multiple_choice_question_choice(
                multiple_choice_question, choice_data
            )
        return multiple_choice_question

    def create_multiple_choice_question_choice(
        self, multiple_choice_question, choice_data
    ):
        """
        multiple_choice_question_choice를 생성하고 반환합니다.

        params:
            multiple_choice_question: MultipleChoiceQuestion
            choice_data: dict
            - choice: str
            - is_correct: bool
        """
        return MultipleChoiceQuestionChoice.objects.create(
            question=multiple_choice_question,
            choice=choice_data.get("choice"),
            is_correct=choice_data.get("is_correct"),
        )


class CourseListCreateView(generics.ListCreateAPIView):
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
        course = self.create_course(serializer)
        for lecture_data in serializer.data.get("lectures"):
            lecture = self.create_lecture(lecture_data, course)
            for topic_data in lecture_data.get("topics"):
                topic = self.create_topic(topic_data, lecture)
                self.handle_topic_type(topic, topic_data)

    def create_course(self, serializer):
        """
        course를 생성하고 반환합니다.

        params:
            serializer: CourseDetailSerializer
            - title: str
            - short_description: str
            - description: dict
            - category: str
            - course_level: str
        """
        return Course.objects.create(
            title=serializer.data.get("title"),
            short_description=serializer.data.get("short_description"),
            description=serializer.data.get("description"),
            category=serializer.data.get("category"),
            course_level=serializer.data.get("course_level"),
        )

    def create_lecture(self, lecture_data, course):
        """
        lecture를 생성하고 반환합니다.

        params:
            course: Course
            lecture_data: dict
            - title: str
            - order: int
        """
        return Lecture.objects.create(
            course=course,
            title=lecture_data.get("title"),
            order=lecture_data.get("order"),
        )

    def create_topic(self, topic_data, lecture):
        """
        topic을 생성하고 반환합니다.

        params:
            lecture: Lecture
            topic_data: dict
            - title: str
            - type: str
            - description: str
            - order: int
            - is_premium: bool
        """
        return Topic.objects.create(
            lecture=lecture,
            title=topic_data.get("title"),
            type=topic_data.get("type"),
            description=topic_data.get("description"),
            order=topic_data.get("order"),
            is_premium=topic_data.get("is_premium"),
        )

    def handle_topic_type(self, topic, topic_data):
        """
        topic의 type에 따라 assignment 또는 quiz를 생성합니다.

        params:
            topic: Topic
            topic_data: dict
            - type: str
            - assignment: dict (optional)
            - multiple_choice_question: dict (optional)
        """
        if topic_data.get("type") == "assignment":
            self.create_assignment(topic, topic_data.get("assignment"))
        elif topic_data.get("type") == "quiz":
            self.create_quiz(topic, topic_data.get("multiple_choice_question"))

    def create_assignment(self, topic, assignment_data):
        """
        assignment를 생성하고 반환합니다.

        params:
            topic: Topic
            assignment_data: dict
            - question: str
        """
        return Assignment.objects.create(
            topic=topic, question=assignment_data.get("question")
        )

    def create_quiz(self, topic, multiple_choice_question_data):
        """
        quiz를 생성하고 반환합니다.

        params:
            topic: Topic
            multiple_choice_question_data: dict
            - question: str
            - multiple_choice_question_choices: list
        """
        multiple_choice_question = MultipleChoiceQuestion.objects.create(
            topic=topic,
            question=multiple_choice_question_data.get("question"),
        )
        for choice_data in multiple_choice_question_data.get(
            "multiple_choice_question_choices"
        ):
            self.create_multiple_choice_question_choice(
                multiple_choice_question, choice_data
            )
        return multiple_choice_question

    def create_multiple_choice_question_choice(
        self, multiple_choice_question, choice_data
    ):
        """
        multiple_choice_question_choice를 생성하고 반환합니다.

        params:
            multiple_choice_question: MultipleChoiceQuestion
            choice_data: dict
            - choice: str
            - is_correct: bool
        """
        return MultipleChoiceQuestionChoice.objects.create(
            question=multiple_choice_question,
            choice=choice_data.get("choice"),
            is_correct=choice_data.get("is_correct"),
        )
