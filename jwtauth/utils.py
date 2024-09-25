import jwt
from datetime import timedelta
from django.conf import settings
from django.utils import timezone


def generate_access_token(user):
    """
    access 토근을 생성하는 함수
    payload에는 user_id, exp, iat를 넣어준다.
    응답으로 받은 토큰은 클라이언트에서 로컬 스토리지에 저장
    """
    payload = {
        "user_id": user.id,
        "exp": timezone.now() + timedelta(minutes=60),
        "iat": timezone.now(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def generate_refresh_token(user):
    """
    refresh 토근을 생성하는 함수
    payload에는 user_id, exp, iat를 넣어준다.
    응답으로 받은 토큰은 클라이언트에서 쿠키에 저장
    """
    payload = {
        "user_id": user.id,
        "exp": timezone.now() + timedelta(minutes=360),
        "iat": timezone.now(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
