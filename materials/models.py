import uuid

from django.db import models

from accounts.models import CustomUser
from courses.models import Course, Topic


def upload_to(instance, filename):
    """
    ImageField를 통해 파일이 업로드될 때 해당 파일의 저장 경로를 동적으로 생성합니다.
    - 모델 인스턴스가 save() 호출될 때, 파일이 저장되기 전 upload_to에 정의된 경로를 생성하기 위해 호출됩니다.
    - ImageField의 upload_to 인자로 전달됩니다.
    - 생성된 경로를 반환하며, 이 경로는 Django가 해당 파일을 저장할 때 사용됩니다.
    - (장점) 사용자 접근성을 높이면서 중복 파일 이름 문제를 해결합니다.
    """
    ext = filename.split(".")[-1]
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
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="이미지를 등록한 사용자",
    )
    image_url = models.URLField(verbose_name="이미지 파일")
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
            self.image_url = "images/default_user_image.jpg"
        if self.course and not self.image_url:
            self.image_url = "images/default_course_image.jpg"
        super().save(*args, **kwargs)


class Video(models.Model):
    topic = models.OneToOneField(
        Topic, on_delete=models.CASCADE, related_name="video", null=True, blank=True
    )
    course = models.OneToOneField(
        Course, on_delete=models.CASCADE, related_name="video", null=True, blank=True
    )
    video_url = models.URLField(verbose_name="비디오 파일")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}"


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
