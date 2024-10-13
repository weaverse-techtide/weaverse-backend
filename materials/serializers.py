import cv2
from PIL import Image as PILImage
from rest_framework import serializers

from .models import Image, Video, VideoEventData


class ImageSerializer(serializers.ModelSerializer):
    """
    이미지 생성(업로드)을 위한 시리얼라이저입니다.
    - 형식, 손상 여부에 대해 유효성 검사를 합니다. 
    """

    class Meta:
        model = Image
        fields = [
            "id",
            "image_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_image_url(self, value):
        allowed_image_extensions = (".png", ".jpg", ".jpeg")

        if not value.name.endswith(allowed_image_extensions):
            raise serializers.ValidationError(
                "지원하지 않는 파일 형식입니다. PNG, JPG, JPEG만 가능합니다."
            )

        try:
            img = PILImage.open(value)
            img.verify()
        except Exception:
            raise serializers.ValidationError("유효한 이미지 파일이 아닙니다.")

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
            "video_url",
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

    def validate_image_url(self, value):
        # 영상 형식과 크기 유효성 검사
        allowed_extensions = ["mp4", "avi", "mov", "wmv"]
        max_size = 100 * 1024 * 1024  # 100MB

        if not value.name.split(".")[-1] in allowed_extensions:
            raise serializers.ValidationError(
                f"허용되지 않는 파일 형식입니다. 다음 형식만 가능합니다: {', '.join(allowed_extensions)}."
            )

        if value.size > max_size:
            raise serializers.ValidationError(
                "파일 크기가 너무 큽니다. 최대 크기는 100MB입니다."
            )

        # 영상 손상 여부 검사
        try:
            cap = cv2.VideoCapture(value)
            if not cap.isOpened():
                raise serializers.ValidationError(
                    "비디오 파일을 열 수 없습니다. 파일이 손상되었을 수 있습니다."
                )

            ret, frame = cap.read()
            if not ret:
                raise serializers.ValidationError(
                    "비디오 파일을 읽을 수 없습니다. 파일이 손상되었을 수 있습니다."
                )

        except Exception as e:
            raise serializers.ValidationError(
                f"비디오 파일 검사 중 오류가 발생했습니다: {str(e)}"
            )
        finally:
            cap.release()

        return value


class VideoEventSerializer(serializers.ModelSerializer):

    video_url = serializers.URLField(
        write_only=True
    )  # 클라이언트가 보내는 video_url을 받기 위한 필드

    class Meta:
        model = VideoEventData
        fields = ["id", "video_url", "duration", "current_time", "event_type"]
        read_only_fields = ["id", "timestamp"]

    def validate_duration(self, value):
        if value < 0:
            raise serializers.ValidationError("올바른 영상 재생시간이 아닙니다.")
        return value

    def validate_current_time(self, value):  # 필드 이름 수정
        if value < 0:
            raise serializers.ValidationError("올바른 영상 현재 재생시간이 아닙니다.")
        return value

    def validate_event_type(self, value):
        """
        event_type 값이 선택된 EVENT_CHOICES 중 하나인지 확인합니다.
        """
        valid_choices = dict(VideoEventData.EVENT_CHOICES).keys()
        if value not in valid_choices:
            raise serializers.ValidationError(f"{value}는 유효한 이벤트가 아닙니다.")
        return value

    def validate(self, data):
        if data["duration"] < data["current_time"]:
            raise serializers.ValidationError("올바른 영상 재생시간 관계가 아닙니다.")
        return data

    def create(self, validated_data):
        """
        VideoEventData를 생성합니다.
        - VideoEventData를 받기 전에, 먼저 S3에 존재하는 Video 인스턴스인지 확인하고
        - 그러하다면 해당 Video 인스턴스와 관계된 VideoEventData를 생성합니다.

        """
        video_url = validated_data.pop("video_url", None)

        try:
            video_instance = Video.objects.get(file=video_url)
        except Video.DoesNotExist:
            raise serializers.ValidationError(
                "해당 URL과 일치하는 영상 파일이 없습니다."
            )
        video_event_data = VideoEventData.objects.create(
            video=video_instance, **validated_data
        )

        return video_event_data


class UserViewEventListSerializer(serializers.ModelSerializer):
    duration_in_minutes = serializers.SerializerMethodField()
    current_time_in_minutes = serializers.SerializerMethodField()

    class Meta:
        model = VideoEventData
        fields = [
            "event_type",
            "duration",
            "current_time",
            "timestamp",
            "duration_in_minutes",  # 분과 초로 변환된 전체 재생시간
            "current_time_in_minutes",  # 분과 초로 변환된 현재 시간
        ]

    def get_duration_in_minutes(self, obj):
        return obj.get_duration_in_minutes()

    def get_current_time_in_minutes(self, obj):
        return obj.get_current_time_in_minutes()
