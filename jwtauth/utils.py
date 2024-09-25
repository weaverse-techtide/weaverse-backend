import jwt
from datetime import timedelta
from django.conf import settings
from django.utils import timezone


def generate_access_token(user):
    payload = {
        "user_id": user.id,
        "exp": timezone.now() + timedelta(minutes=60),
        "iat": timezone.now(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def generate_refresh_token(user):
    payload = {
        "user_id": user.id,
        "exp": timezone.now() + timedelta(minutes=360),
        "iat": timezone.now(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
