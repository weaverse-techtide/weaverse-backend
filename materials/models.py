from courses.models import Course, Topic
from django.db import models


class Image(models.Model):
    course = models.OneToOneField(
        Course, on_delete=models.CASCADE, related_name="images"
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
