from accounts.models import CustomUser
from courses.models import Course, Topic
from rest_framework import serializers

from .models import Image, Video


class ImageSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Image
        fields = [
            "id",
            "course",
            "course_title",
            "title",
            "file",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_course(self, value):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            if not request.user.is_staff and value.tutor != request.user:
                raise serializers.ValidationError(
                    "이 course에 이미지를 넣을 권한이 없습니다."
                )
        return value


class VideoSerializer(serializers.ModelSerializer):
    topic_title = serializers.CharField(source="topic.title", read_only=True)
    course_title = serializers.CharField(source="topic.course.title", read_only=True)

    class Meta:
        model = Video
        fields = [
            "id",
            "topic",
            "topic_title",
            "course_title",
            "title",
            "file",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_topic(self, value):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            if not request.user.is_staff and value.course.tutor != request.user:
                raise serializers.ValidationError(
                    "이 topic에 영상을 넣을 권한이 없습니다."
                )
        return value


class WatchHistorySerializer(serializers.Serializer):

    pass
