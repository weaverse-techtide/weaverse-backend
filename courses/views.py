from django.db import transaction
from rest_framework import generics

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


class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    permission_classes = [IsStaffOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CourseDetailSerializer
        return CourseSummarySerializer

    @transaction.atomic
    def perform_create(self, serializer):
        course = self.create_course(serializer)
        self.create_lectures(serializer.data.get("lectures"), course)

    def create_course(self, serializer):
        return Course.objects.create(
            title=serializer.data.get("title"),
            short_description=serializer.data.get("short_description"),
            description=serializer.data.get("description"),
            category=serializer.data.get("category"),
            course_level=serializer.data.get("course_level"),
        )

    def create_lectures(self, lectures_data, course):
        for lecture_data in lectures_data:
            lecture = Lecture.objects.create(
                course=course,
                title=lecture_data.get("title"),
                order=lecture_data.get("order"),
            )
            self.create_topics(lecture_data.get("topics"), lecture)

    def create_topics(self, topics_data, lecture):
        for topic_data in topics_data:
            topic = Topic.objects.create(
                lecture=lecture,
                title=topic_data.get("title"),
                type=topic_data.get("type"),
                description=topic_data.get("description"),
                order=topic_data.get("order"),
                is_premium=topic_data.get("is_premium"),
            )
            self.handle_topic_type(topic, topic_data)

    def handle_topic_type(self, topic, topic_data):
        if topic_data.get("type") == "assignment":
            Assignment.objects.create(
                topic=topic,
                question=topic_data.get("assignment").get("question"),
            )
        elif topic_data.get("type") == "quiz":
            self.create_quiz(topic, topic_data.get("multiple_choice_question"))

    def create_quiz(self, topic, multiple_choice_question_data):
        multiple_choice_question = MultipleChoiceQuestion.objects.create(
            topic=topic,
            question=multiple_choice_question_data.get("question"),
        )
        for choice_data in multiple_choice_question_data.get(
            "multiple_choice_question_choices"
        ):
            MultipleChoiceQuestionChoice.objects.create(
                question=multiple_choice_question,
                choice=choice_data.get("choice"),
                is_correct=choice_data.get("is_correct"),
            )
