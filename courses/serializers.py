from rest_framework import serializers

from .models import (
    Assignment,
    Course,
    Curriculum,
    Lecture,
    MultipleChoiceQuestion,
    MultipleChoiceQuestionChoice,
    Topic,
)


class AssignmentSerializer(serializers.ModelSerializer):
    """
    Assignment 모델을 위한 Serializer입니다
    """

    class Meta:
        model = Assignment
        fields = ["question", "created_at", "updated_at", "id"]
        read_only_fields = ["created_at", "updated_at", "id"]


class MultipleChoiceQuestionChoiceSerializer(serializers.ModelSerializer):
    """
    MultipleChoiceQuestionChoice 모델을 위한 Serializer입니다
    """

    class Meta:
        model = MultipleChoiceQuestionChoice
        fields = ["id", "choice", "is_correct", "created_at", "updated_at", "id"]
        read_only_fields = ["created_at", "updated_at", "id"]


class MultipleChoiceQuestionSerializer(serializers.ModelSerializer):
    """
    MultipleChoiceQuestion 모델을 위한 Serializer입니다
    """

    multiple_choice_question_choices = MultipleChoiceQuestionChoiceSerializer(many=True)

    class Meta:
        model = MultipleChoiceQuestion
        fields = [
            "id",
            "question",
            "created_at",
            "updated_at",
            "multiple_choice_question_choices",
        ]
        read_only_fields = ["created_at", "updated_at", "id"]


class TopicSerializer(serializers.ModelSerializer):
    """
    Topic 모델을 위한 Serializer입니다
    """

    multiple_choice_question = MultipleChoiceQuestionSerializer(required=False)
    assignment = AssignmentSerializer(required=False)
    video_url = serializers.SerializerMethodField()
    video_id = serializers.IntegerField(write_only=True, required=False)
    video_duration = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = [
            "id",
            "title",
            "type",
            "order",
            "is_premium",
            "created_at",
            "updated_at",
            "multiple_choice_question",
            "assignment",
            "video_url",
            "video_id",
            "video_duration",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "id",
            "video_url",
            "video_duration",
        ]

    def get_video_url(self, obj):
        if getattr(obj, "video", None):
            return obj.video.url
        return None

    def get_video_duration(self, obj):
        if getattr(obj, "video", None):
            return 0
        return None


class LectureSerializer(serializers.ModelSerializer):
    """
    Lecture 모델을 위한 Serializer입니다
    """

    topics = TopicSerializer(many=True)

    class Meta:
        model = Lecture
        fields = ["id", "title", "order", "created_at", "updated_at", "topics"]
        read_only_fields = ["created_at", "updated_at", "id"]


class CourseDetailSerializer(serializers.ModelSerializer):
    """
    Course 모델을 위한 Serializer입니다
    """

    video_id = serializers.IntegerField(write_only=True)
    thumbnail_id = serializers.IntegerField(write_only=True)
    lectures = LectureSerializer(
        many=True,
        required=False,
    )
    video_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    author_image = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()
    author_id = serializers.SerializerMethodField()
    author_introduction = serializers.SerializerMethodField()

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
            "skill_level",
            "price",
            "thumbnail_id",
            "video_id",
            "video_url",
            "thumbnail_url",
            "author_image",
            "author_name",
            "author_id",
            "author_introduction",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "id",
            "video_url",
            "thumbnail_url",
            "author_image",
            "author_name",
            "author_id",
            "author_introduction",
        ]

    def get_author_image(self, obj):
        if getattr(obj.author, "image", None):
            return obj.author.image.url
        return None

    def get_author_name(self, obj):
        return obj.author.nickname

    def get_video_url(self, obj):
        if getattr(obj, "video", None):
            return obj.video.url
        return None

    def get_thumbnail_url(self, obj):
        if getattr(obj, "thumbnail", None):
            return obj.thumbnail.url
        return None

    def get_author_id(self, obj):
        return obj.author.id

    def get_author_introduction(self, obj):
        return (
            obj.author.introduction if obj.author.introduction else "소개가 없습니다."
        )


class CourseSummarySerializer(serializers.ModelSerializer):
    """
    Course 모델을 위한 Serializer입니다
    """

    lectures_count = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    author_image = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "short_description",
            "category",
            "created_at",
            "updated_at",
            "skill_level",
            "lectures_count",
            "thumbnail",
            "author_image",
            "author_name",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "id",
            "lectures_count",
            "thumbnail",
            "author_image",
            "author_name",
        ]

    def get_lectures_count(self, obj):
        return obj.lectures.count()

    def get_thumbnail(self, obj):
        return obj.get_thumbnail()

    def get_author_image(self, obj):
        if getattr(obj.author, "image", None):
            return obj.author.image.url
        return "https://paullab.co.kr/images/weniv-licat.png"

    def get_author_name(self, obj):
        return obj.author.nickname


class CurriculumReadSerializer(serializers.ModelSerializer):
    """
    Curriculum 모델을 조회하기 위한 Serializer입니다. 직렬화 할 때만 사용합니다.
    """

    courses = CourseSummarySerializer(
        many=True,
    )

    class Meta:
        model = Curriculum
        fields = [
            "id",
            "name",
            "price",
            "description",
            "courses",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "id"]


class CurriculumCreateAndUpdateSerializer(serializers.ModelSerializer):
    """
    Curriculum 모델을 생성 및 수정을 위한 Serializer입니다. 역직렬화 할 때만 사용합니다.
    """

    courses_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )

    class Meta:
        model = Curriculum
        fields = ["id", "name", "price", "description", "courses_ids"]
        read_only_fields = ["created_at", "updated_at", "id"]


class CurriculumSummarySerializer(serializers.ModelSerializer):
    """
    Curriculum 모델을 위한 Serializer입니다. 직렬화 할 때만 사용합니다.
    """

    author_image = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()
    courses_count = serializers.SerializerMethodField()

    class Meta:
        model = Curriculum
        fields = [
            "id",
            "name",
            "price",
            "created_at",
            "updated_at",
            "author_image",
            "author_name",
            "category",
            "skill_level",
            "description",
            "courses_count",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "id",
            "author_image",
            "author_name",
            "category",
            "skill_level",
            "description",
            "courses_count",
        ]

    def get_author_image(self, obj):
        if getattr(obj.author, "image", None):
            return obj.author.image.url
        return "https://paullab.co.kr/images/weniv-licat.png"

    def get_author_name(self, obj):
        return obj.author.nickname

    def get_courses_count(self, obj):
        return obj.courses.count()
