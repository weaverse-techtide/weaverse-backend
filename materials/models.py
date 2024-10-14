from accounts.models import CustomUser
from courses.models import Course, Topic
from django.conf import settings
from django.db import models


class Image(models.Model):
    """
    이미지 객체를 위해 작성된 모델입니다.
    - 관계: Course(1:1), CustomUser(1:1), CustomUser(1:N)를 갖습니다.
    - 삭제: 소프트 삭제를 위해 불린 필드를 갖습니다.
    - 생성: 지정한 이미지 파일이 없다면 디폴트 값으로 저장됩니다.
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
        null=True,
        blank=True,
    )

    image_url = models.ImageField(
        upload_to="images/", blank=True, null=True, verbose_name="이미지 파일"
    )
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

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
    """
    동영상 객체를 위해 작성된 모델입니다.
    - 관계: Topic(1:1), Course(1:1)를 갖습니다.
    - 삭제: 소프트 삭제를 위해 불린 필드를 갖습니다.
    - 생성: 지정한 이미지 파일이 없다면 디폴트 값으로 저장됩니다.
    """

    topic = models.OneToOneField(
        Topic, on_delete=models.CASCADE, related_name="video", null=True, blank=True
    )
    course = models.OneToOneField(
        Course, on_delete=models.CASCADE, related_name="video", null=True, blank=True
    )
    video_url = models.FileField(
        upload_to="videos/", blank=True, null=True, verbose_name="비디오 파일"
    )
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

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
    """
    특정 사용자에 대한 동영상 이벤트 객체를 위해 작성된 모델입니다.
    - 관계: Course(1:1), CustomUser(1:1), CustomUser(1:N)를 갖습니다.
    - 삭제: 소프트 삭제를 위해 불린 필드를 갖습니다.
    - 생성: 지정한 이미지 파일이 없다면 디폴트 값으로 저장됩니다.
    - 변환: 동영상 전체 길이와 현재 재생 시점을 분과 초로 변환합니다.
    """

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
        verbose_name="시청 기록의 해당 동영상",
    )

    event_type = models.CharField(
        max_length=20, choices=EVENT_CHOICES, verbose_name="이벤트 유형"
    )
    duration = models.FloatField(verbose_name="동영상 전체 길이")
    current_time = models.FloatField(verbose_name="현재 재생 위치")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="이벤트 발생 시간")

    class Meta:
        ordering = ["-timestamp"]

    def get_duration_in_minutes(self):
        """
        분과 초로 변환된 동영상 전체 재생 시간을 반환합니다.
        """
        minutes = int(self.duration // 60)
        seconds = int(self.duration % 60)
        return f"{minutes}분 {seconds}초"

    def get_current_time_in_minutes(self):
        """
        분과 초로 변환된 동영상 현재 재생 시점을 반환합니다.
        """
        minutes = int(self.current_time // 60)
        seconds = int(self.current_time % 60)
        return f"{minutes}분 {seconds}초"

    def __str__(self):
        return f"{self.event_type} at {self.get_current_time_in_minutes()}/{self.get_duration_in_minutes()}"
