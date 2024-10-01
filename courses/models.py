from django.db import models


class Curriculum(models.Model):
    name = models.CharField(max_length=255, verbose_name="커리큘럼 이름")
    description = models.TextField(verbose_name="설명")
    price = models.PositiveIntegerField(verbose_name="가격")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    category_choices = [
        ("JavaScript", "JavaScript"),
        ("Python", "Python"),
        ("Django", "Django"),
        ("React", "React"),
        ("Vue.js", "Vue.js"),
        ("Node.js", "Node.js"),
        ("AWS", "AWS"),
        ("Docker", "Docker"),
        ("DB", "DB"),
    ]
    course_level_choices = [
        ("beginner", "초급"),
        ("intermediate", "중급"),
        ("advanced", "고급"),
    ]

    curriculum = models.ForeignKey(
        Curriculum, on_delete=models.SET_NULL, null=True, related_name="courses"
    )
    title = models.CharField(max_length=255, verbose_name="코스 제목")
    short_description = models.TextField(verbose_name="간단한 설명")
    description = models.JSONField(verbose_name="설명")
    category = models.CharField(
        max_length=255,
        verbose_name="카테고리",
        choices=category_choices,
        default="JavaScript",
    )
    course_level = models.CharField(
        max_length=255,
        verbose_name="난이도",
        choices=course_level_choices,
        default="beginner",
    )
    price = models.PositiveIntegerField(verbose_name="가격")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}"


class Lecture(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="lectures"
    )
    title = models.CharField(max_length=255, verbose_name="강의 제목")
    order = models.PositiveIntegerField(verbose_name="순서")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Topic(models.Model):
    topic_type_choices = [
        ("video", "동영상"),
        ("article", "글"),
        ("assignment", "과제"),
        ("quiz", "퀴즈"),
    ]

    lecture = models.ForeignKey(
        Lecture, on_delete=models.CASCADE, related_name="topics"
    )
    title = models.CharField(max_length=255, verbose_name="주제 제목")
    type = models.CharField(
        max_length=255,
        verbose_name="주제 타입",
        choices=topic_type_choices,
        default="video",
    )
    description = models.TextField(verbose_name="설명")
    order = models.PositiveIntegerField(verbose_name="순서")
    is_premium = models.BooleanField(verbose_name="프리미엄 여부", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.lecture.title} - {self.title}"


class MultipleChoiceQuestion(models.Model):
    topic = models.OneToOneField(
        Topic, on_delete=models.CASCADE, related_name="multiple_choice_question"
    )
    question = models.TextField(verbose_name="문제")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.topic.title} - {self.question}"


class MultipleChoiceQuestionChoice(models.Model):
    question = models.ForeignKey(
        MultipleChoiceQuestion,
        on_delete=models.CASCADE,
        related_name="multiple_choice_question_choices",
    )
    choice = models.CharField(max_length=255, verbose_name="선택지")
    is_correct = models.BooleanField(verbose_name="정답 여부")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.question.question} - {self.choice}"


class Assignment(models.Model):
    topic = models.OneToOneField(
        Topic, on_delete=models.CASCADE, related_name="assignment"
    )
    question = models.TextField(verbose_name="문제")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.topic.title} - {self.question}"
