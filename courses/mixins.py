from django.db import transaction

from .models import (
    Assignment,
    Course,
    Lecture,
    MultipleChoiceQuestion,
    MultipleChoiceQuestionChoice,
    Topic,
)


class CourseMixin:
    """
    Course 모델과 관련된 기능을 제공하는 Mixin 클래스입니다
    """

    @transaction.atomic
    def create_course_with_lectures_and_topics(self, course_data, lectures_data):
        """
        course 및 하위 모델 lecture, topic, assignment, quiz 등을 함께 생성합니다.
        """

        course = self._create_course(course_data)
        for lecture_data in lectures_data:
            lecture = self._create_lecture(lecture_data, course)
            for topic_data in lecture_data.get("topics", []):
                topic = self._create_topic(topic_data, lecture)
                self._handle_topic_type(topic, topic_data)
        return course

    @transaction.atomic
    def update_course_with_lectures_and_topics(
        self, course, course_data, lectures_data
    ):
        """
        course 및 하위 모델 lecture, topic, assignment, quiz 등을 함께 수정합니다.
        """

        course.title = course_data.get("title")
        course.short_description = course_data.get("short_description")
        course.description = course_data.get("description")
        course.category = course_data.get("category")
        course.course_level = course_data.get("course_level")
        course.save()

        course.lectures.all().delete()
        for lecture_data in lectures_data:
            lecture = self._create_lecture(lecture_data, course)
            for topic_data in lecture_data.get("topics", []):
                topic = self._create_topic(topic_data, lecture)
                self._handle_topic_type(topic, topic_data)

    def _create_course(self, course_data):
        """
        course 인스턴스를 생성합니다.
        """

        return Course.objects.create(
            title=course_data.get("title"),
            short_description=course_data.get("short_description"),
            description=course_data.get("description"),
            category=course_data.get("category"),
            course_level=course_data.get("course_level"),
        )

    def _create_lecture(self, lecture_data, course):
        """
        lecture 인스턴스를 생성합니다.
        """

        return Lecture.objects.create(
            course=course,
            title=lecture_data.get("title"),
            order=lecture_data.get("order"),
        )

    def _create_topic(self, topic_data, lecture):
        """
        topic 인스턴스를 생성합니다.
        """

        return Topic.objects.create(
            lecture=lecture,
            title=topic_data.get("title"),
            type=topic_data.get("type"),
            description=topic_data.get("description"),
            order=topic_data.get("order"),
            is_premium=topic_data.get("is_premium"),
        )

    def _handle_topic_type(self, topic, topic_data):
        """
        topic의 type에 따라 assignment 또는 quiz를 생성합니다.
        """

        if topic_data.get("type") == "assignment":
            self._create_assignment(topic, topic_data.get("assignment"))
        elif topic_data.get("type") == "quiz":
            self._create_quiz(topic, topic_data.get("multiple_choice_question"))

    def _create_assignment(self, topic, assignment_data):
        """
        assignment 인스턴스를 생성합니다.
        """

        return Assignment.objects.create(
            topic=topic, question=assignment_data.get("question")
        )

    def _create_quiz(self, topic, multiple_choice_question_data):
        """
        quiz 인스턴스를 생성합니다.
        """

        multiple_choice_question = MultipleChoiceQuestion.objects.create(
            topic=topic,
            question=multiple_choice_question_data.get("question"),
        )
        for choice_data in multiple_choice_question_data.get(
            "multiple_choice_question_choices", []
        ):
            self._create_multiple_choice_question_choice(
                multiple_choice_question, choice_data
            )
        return multiple_choice_question

    def _create_multiple_choice_question_choice(
        self, multiple_choice_question, choice_data
    ):
        """
        multiple_choice_question_choice 인스턴스를 생성합니다.
        """

        return MultipleChoiceQuestionChoice.objects.create(
            question=multiple_choice_question,
            choice=choice_data.get("choice"),
            is_correct=choice_data.get("is_correct"),
        )
