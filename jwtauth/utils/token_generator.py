import jwt
from datetime import timedelta
from django.conf import settings
from django.utils import timezone


def generate_access_token(user):
    """
    사용자 정보를 받아서 access token을 생성합니다.
    """
    payload = {
        "user_id": user.id,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "iat": timezone.now(),
        "nickname": user.nickname,
        "email": user.email,
        # "image": user.image,
        "exp": timezone.now() + timedelta(minutes=30),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def generate_refresh_token(user):
    """
    사용자 정보를 받아서 refresh token을 생성합니다.
    """
    payload = {
        "user_id": user.id,
        "exp": timezone.now() + timedelta(days=14),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
