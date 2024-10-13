import uuid

from django.db import models

from accounts.models import CustomUser
from courses.models import Course, Topic
from django.conf import settings
from django.db import models


def upload_to(instance, filename):
    """
    이미지 파일을 S3에 업로드할 때 사용할 경로를 동적으로 생성합니다.
    UUID를 사용하여 중복 파일명을 피합니다.
    """
    ext = filename.split(".")[-1]  # 파일 확장자 추출
    return f"images/{uuid.uuid4()}.{ext}"


class Image(models.Model):
    """
    이미지 객체를 위해 작성된 모델입니다.
    """

    course = models.OneToOneField(
        Course,
        on_delete=models.CASCADE,
        related_name="image",
        null=True,
        blank=True,
    )
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="image",
        null=True,
        blank=True,
    )
    image_url = models.ImageField(upload_to=upload_to, blank=True, null=True, verbose_name="이미지 파일")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"{self.user}'s Image"
        elif self.course:
            return f"Course Image for {self.course}"
        return "Image"

    def save(self, *args, **kwargs):

        if self.user and not self.image_url:
            self.image_url = f"{settings.MEDIA_URL}images/default_user_image.jpg"
        if self.course and not self.image_url:
            self.image_url = f"{settings.MEDIA_URL}images/default_user_image.jpg"
        super().save(*args, **kwargs)


class Video(models.Model):
    topic = models.OneToOneField(
        Topic, on_delete=models.CASCADE, related_name="video", null=True, blank=True
    )
    course = models.OneToOneField(
        Course, on_delete=models.CASCADE, related_name="video", null=True, blank=True
    )
    video_url = models.URLField(blank=True, null=True, verbose_name="비디오 파일")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.topic:
            return f"{self.topic}'s Video"
        elif self.course:
            return f"Course Video for {self.course}"
        return "Video"
    
    def save(self, *args, **kwargs):
        if not self.video_url:
            self.video_url = f"{settings.MEDIA_URL}videos/default_video.mp4"

        super().save(*args, **kwargs)


class VideoEventData(models.Model):
    EVENT_CHOICES = [
        ("pause", "Paused"),
        ("ended", "Ended"),
        ("leave", "Left Page"),
    ]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="video_event_datas",
        verbose_name="시청 기록의 해당 사용자",
    )

    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="video_event_datas",
        verbose_name="시청 기록의 해당 비디오",
    )

    event_type = models.CharField(
        max_length=20, choices=EVENT_CHOICES, verbose_name="이벤트 유형"
    )
    duration = models.FloatField(verbose_name="비디오 전체 길이")  # 초 단위로 저장
    current_time = models.FloatField(verbose_name="현재 재생 위치")  # 초 단위로 저장
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="이벤트 발생 시간")

    def get_duration_in_minutes(self):
        """
        분과 초로 변환된 영상 재생 시간을 반환합니다.
        """
        minutes = int(self.duration // 60)
        seconds = int(self.duration % 60)
        return f"{minutes}분 {seconds}초"

    def get_current_time_in_minutes(self):
        """
        분과 초로 변환된 현재 재생 시간을 반환합니다.
        """
        minutes = int(self.current_time // 60)
        seconds = int(self.current_time % 60)
        return f"{minutes}분 {seconds}초"

    def __str__(self):
        return f"{self.event_type} at {self.get_current_time_in_minutes()}/{self.get_duration_in_minutes()}"
