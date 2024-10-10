from courses.models import Course, Topic
from django.db import models


class Image(models.Model):
    course = models.OneToOneField(
        Course, on_delete=models.CASCADE, related_name="image"
    )
    title = models.CharField(max_length=255, verbose_name="이미지 제목")
    file = models.ImageField(upload_to="images/", verbose_name="이미지 파일")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.topic.title} - {self.title}"


class Video(models.Model):
    topic = models.OneToOneField(Topic, on_delete=models.CASCADE, related_name="video")
    title = models.CharField(max_length=255, verbose_name="비디오 제목")
    file = models.FileField(upload_to="videos/", verbose_name="비디오 파일")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.topic.title} - {self.title}"


class VideoEventData(models.Model):
    EVENT_CHOICES = [
        ("pause", "Paused"),
        ("ended", "Ended"),
        ("leave", "Left Page"),
    ]

    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="video_event_datas",
        verbose_name="해당 비디오",
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
