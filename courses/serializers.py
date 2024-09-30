from rest_framework import serializers

from .models import (
    Assignment,
    Course,
    Lecture,
    MultipleChoiceQuestion,
    MultipleChoiceQuestionChoice,
    Topic,
)


class AssignmentSerializer(serializers.ModelSerializer):
    """
    Assignment 모델을 위한 Serializer입니다
    """

    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Assignment
        fields = ["id", "question", "created_at", "updated_at"]


class MultipleChoiceQuestionChoiceSerializer(serializers.ModelSerializer):
    """
    MultipleChoiceQuestionChoice 모델을 위한 Serializer입니다
    """

    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = MultipleChoiceQuestionChoice
        fields = ["id", "choice", "is_correct", "created_at", "updated_at"]


class MultipleChoiceQuestionSerializer(serializers.ModelSerializer):
    """
    MultipleChoiceQuestion 모델을 위한 Serializer입니다
    """

    multiple_choice_question_choices = MultipleChoiceQuestionChoiceSerializer(many=True)

    class Meta:
        model = MultipleChoiceQuestion
        fields = [
            "question",
            "created_at",
            "updated_at",
            "multiple_choice_question_choices",
        ]


class TopicSerializer(serializers.ModelSerializer):
    """
    Topic 모델을 위한 Serializer입니다
    """

    id = serializers.IntegerField(read_only=True)
    multiple_choice_question = MultipleChoiceQuestionSerializer(required=False)
    assignment = AssignmentSerializer(required=False)

    class Meta:
        model = Topic
        fields = [
            "id",
            "title",
            "type",
            "description",
            "order",
            "is_premium",
            "created_at",
            "updated_at",
            "multiple_choice_question",
            "assignment",
        ]


class LectureSerializer(serializers.ModelSerializer):
    """
    Lecture 모델을 위한 Serializer입니다
    """

    id = serializers.IntegerField(read_only=True)
    topics = TopicSerializer(many=True)

    class Meta:
        model = Lecture
        fields = ["id", "title", "order", "created_at", "updated_at", "topics"]


class CourseDetailSerializer(serializers.ModelSerializer):
    """
    Course 모델을 위한 Serializer입니다
    """

    id = serializers.IntegerField(read_only=True)
    lectures = LectureSerializer(
        many=True,
        required=False,
    )

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "short_description",
            "description",
            "category",
            "created_at",
            "updated_at",
            "lectures",
            "course_level",
        ]


class CourseSummarySerializer(serializers.ModelSerializer):
    """
    Course 모델을 위한 Serializer입니다
    """

    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "short_description",
            "category",
            "created_at",
            "updated_at",
            "course_level",
        ]
