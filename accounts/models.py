from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.apps import apps
from django.contrib import auth
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _


class CustomUserManager(UserManager):
    """
    사용자 모델의 생성 로직을 커스텀마이징합니다.
    - CustomUser에서 설정변경한 사용한 식별자(email)로 사용자 인스턴스를 생성하도록 합니다.
    """

    def _create_user(self, email, password, **extra_fields):
        """
        사용자 유형과 관계없이 실제로 사용자를 생성해 넘겨줍니다.
        """
        if not email:
            raise ValueError("Email is required.")
        email = self.normalize_email(email)
        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        일반 사용자를 생성합니다.
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """
        슈퍼 사용자를 생성합니다.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra_fields)

    def create_staff_user(self, email, password=None, **extra_fields):
        """
        관리자(강사)를 생성합니다.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def with_perm(
        self, perm, is_active=True, include_superusers=True, backend=None, obj=None
    ):
        """
        특정한 권한을 가진 사용자를 쉽게 필터링합니다.
        - 먼저, 설정된 인증 백엔드 확인하고 유효성 검사, 로딩합니다.
        - 로딩된 백엔드에 with_perm이 있다면 그것을 호출하고 없다면 빈 쿼리셋을 반환합니다.

        """
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    "You have multiple authentication backends configured and "
                    "therefore must provide the `backend` argument."
                )
        elif not isinstance(backend, str):
            raise TypeError(
                "backend must be a dotted import path string (got %r)." % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, "with_perm"):
            return backend.with_perm(
                perm,  # 권한 인스턴스 (형식: "<앱 레이블>.<권한 코드명>")
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()


class CustomUser(AbstractUser):
    """
    AbstractUser을 사용하여 User를 커스텀마이징합니다.
    - 사용자 식별자 변경(username -> email)
    - 사용자 매니저 지정(UserManager -> CustomUserManager)
    """

    username = None
    email = models.EmailField(_("email address"), unique=True)  # 필드를 기본키로 지정

    USERNAME_FIELD = "email"  # 인증시 사용할 필드 지정
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
