from django.db import models


class Curriculum(models.Model):
    """
    커리큘럼 모델입니다.
    """

    name = models.CharField(max_length=255, verbose_name="커리큘럼 이름")
    description = models.TextField(verbose_name="설명")
    price = models.PositiveIntegerField(verbose_name="가격")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "커리큘럼"
        verbose_name_plural = "커리큘럼 목록"


class Course(models.Model):
    """
    코스 모델입니다.
    """

    category_choices = [
        ("JavaScript", "JavaScript"),
        ("Python", "Python"),
        ("Django", "Django"),
        ("React", "React"),
        ("Vue", "Vue"),
        ("Node", "Node"),
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
        Curriculum,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses",
        verbose_name="커리큘럼",
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
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    def get_thumbnail(self):
        if hasattr(self, "images") and self.images.exists():
            return self.images.first().file.url
        return "https://www.gravatar.com/avatar/205e460b479e2e5b48aec077"

    def update(self, **kwargs):
        """
        코스 정보를 수정합니다.
        수정 가능한 필드:
        - title: 코스 제목
        - short_description: 간단한 설명
        - description: 설명
        - category: 카테고리
        - course_level: 난이도
        - price: 가격
        """
        for key, value in kwargs.items():
            if key not in [
                "title",
                "short_description",
                "description",
                "category",
                "course_level",
                "price",
            ]:
                continue
            setattr(self, key, value)
        self.save()

    def __str__(self):
        return f"{self.title}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "코스"
        verbose_name_plural = "코스 목록"


class Lecture(models.Model):
    """
    강의 모델입니다.
    """

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="lectures", verbose_name="코스"
    )
    title = models.CharField(max_length=255, verbose_name="강의 제목")
    order = models.PositiveIntegerField(verbose_name="순서")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    class Meta:
        ordering = ["order"]
        verbose_name = "강의"
        verbose_name_plural = "강의 목록"


class Topic(models.Model):
    """
    주제 모델입니다.
    """

    topic_type_choices = [
        ("video", "동영상"),
        ("article", "글"),
        ("assignment", "과제"),
        ("quiz", "퀴즈"),
    ]

    lecture = models.ForeignKey(
        Lecture, on_delete=models.CASCADE, related_name="topics", verbose_name="강의"
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
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    def __str__(self):
        return f"{self.lecture.title} - {self.title}"

    class Meta:
        ordering = ["order"]
        verbose_name = "주제"
        verbose_name_plural = "주제 목록"


class MultipleChoiceQuestion(models.Model):
    """
    객관식 문제 모델입니다.
    """

    topic = models.OneToOneField(
        Topic,
        on_delete=models.CASCADE,
        related_name="multiple_choice_question",
        verbose_name="주제",
    )
    question = models.TextField(verbose_name="문제")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    def __str__(self):
        return f"{self.topic.title} - {self.question}"

    class Meta:
        verbose_name = "객관식 문제"
        verbose_name_plural = "객관식 문제 목록"


class MultipleChoiceQuestionChoice(models.Model):
    """
    객관식 문제 선택지 모델입니다.
    """

    question = models.ForeignKey(
        MultipleChoiceQuestion,
        on_delete=models.CASCADE,
        related_name="multiple_choice_question_choices",
        verbose_name="문제",
    )
    choice = models.CharField(max_length=255, verbose_name="선택지")
    is_correct = models.BooleanField(verbose_name="정답 여부")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    def __str__(self):
        return f"{self.question.question} - {self.choice}"


class Assignment(models.Model):
    """
    과제 모델입니다.
    """

    topic = models.OneToOneField(
        Topic, on_delete=models.CASCADE, related_name="assignment", verbose_name="주제"
    )
    question = models.TextField(verbose_name="문제")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    def __str__(self):
        return f"{self.topic.title} - {self.question}"

    class Meta:
        verbose_name = "과제"
        verbose_name_plural = "과제 목록"
