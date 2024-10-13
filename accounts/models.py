from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class CustomUserManager(UserManager):
    """
    사용자 모델의 생성 로직을 커스텀마이징합니다.
    - CustomUser에서 설정변경한 사용한 식별자(email)로 사용자 인스턴스를 생성하도록 합니다.
    """

    def _create_user(self, email, password, nickname, **extra_fields):
        """
        사용자 유형과 관계없이 사용자를 실제로 생성하고 반환합니다.
        """
        if not email:
            raise ValueError("이메일은 필수로 입력하셔야 합니다.")
        if not nickname:
            raise ValueError("닉네임은 필수로 입력하셔야 합니다.")
        email = self.normalize_email(email)
        user = self.model(email=email, nickname=nickname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, nickname, **extra_fields):
        """
        학생(student)를 생성합니다.
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, nickname, **extra_fields)

    def create_staff(self, email, password, nickname, **extra_fields):
        """
        스태프(tutor)를 생성합니다.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Staff user must have is_staff=True.")
        return self._create_user(email, password, nickname, **extra_fields)

    def create_superuser(self, email, password, nickname, **extra_fields):
        """
        관리자(superuser)를 생성합니다.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, nickname, **extra_fields)


class CustomUser(AbstractUser):
    """
    AbstractUser을 사용하여 User를 커스텀마이징합니다.
    - 사용자 식별자 변경(username -> email)
    - 사용자 매니저 지정(UserManager -> CustomUserManager)
    """

    # 미사용할 기본 필드
    username = None
    date_joined = None

    email = models.EmailField(unique=True, verbose_name="이메일")  # 기본키 변경

    # 추가 필드
    nickname = models.CharField(max_length=20, unique=True, verbose_name="닉네임")
    phone_number = models.CharField(
        max_length=20, null=True, blank=True, verbose_name="연락처"
    )
    introduction = models.TextField(
        max_length=20, null=True, blank=True, verbose_name="자기소개"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성 일자")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="갱신 일자")

    students = models.ManyToManyField(  # 특정 사용자(튜터)가 갖는 여러 명의 학생들
        "self",
        symmetrical=False,  # 비대칭 관계(학생과 튜터는 독립적인 관계)
        related_name="tutors",  # 특정 사용자(학생)이 갖는 여러 명의 튜터들
        related_query_name="tutor",  # 쿼리셋의 필터링
        limit_choices_to={"is_staff": False},  # 학생만 선택할 수 있도록 제한
        blank=True,  # 비어 있을 수 있도록 허용
        verbose_name="수강 학생들",  # 사용자에게 보일 이름
    )

    # 인증시 사용할 필드
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nickname"]  # email, password 자동 포함

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_image_url(self):
        if getattr(self, "image", None):
            return self.image.image_url
        return "https://paullab.co.kr/images/weniv-licat.png"
