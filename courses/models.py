from django.db import models
from accounts.models import CustomUser


class Curriculum(models.Model):
    name = models.CharField(max_length=255, verbose_name="커리큘럼 이름")
    description = models.TextField(verbose_name="설명")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    curriculum = models.ForeignKey(
        Curriculum, on_delete=models.SET_NULL, null=True, related_name="courses"
    )
    title = models.CharField(max_length=255, verbose_name="코스 제목")
    description = models.TextField(verbose_name="설명")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.curriculum.name} - {self.title}"


class Lecture(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="lectures"
    )
    title = models.CharField(max_length=255, verbose_name="강의 제목")
    description = models.TextField(verbose_name="설명")
    order = models.PositiveIntegerField(verbose_name="순서")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Topic(models.Model):
    lecture = models.ForeignKey(
        Lecture, on_delete=models.CASCADE, related_name="topics"
    )
    title = models.CharField(max_length=255, verbose_name="주제 제목")
    description = models.TextField(verbose_name="설명")
    order = models.PositiveIntegerField(verbose_name="순서")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.lecture.title} - {self.title}"


class Mission(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="missions")
    title = models.CharField(max_length=255, verbose_name="미션 제목")
    description = models.TextField(verbose_name="설명")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.topic.title} - {self.title}"
