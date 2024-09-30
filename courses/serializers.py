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
    class Meta:
        model = Assignment
        fields = ["question", "created_at", "updated_at"]


class MultipleChoiceQuestionChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultipleChoiceQuestionChoice
        fields = ["choice", "is_correct", "created_at", "updated_at"]


class MultipleChoiceQuestionSerializer(serializers.ModelSerializer):
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
    multiple_choice_question = MultipleChoiceQuestionSerializer(required=False)
    assignment = AssignmentSerializer(required=False)

    class Meta:
        model = Topic
        fields = [
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
    topics = TopicSerializer(many=True)

    class Meta:
        model = Lecture
        fields = ["title", "order", "created_at", "updated_at", "topics"]


class CourseSerializer(serializers.ModelSerializer):
    lectures = LectureSerializer(
        many=True,
        required=False,
    )

    class Meta:
        model = Course
        fields = [
            "title",
            "short_description",
            "description",
            "category",
            "created_at",
            "updated_at",
            "lectures",
            "course_level",
        ]
