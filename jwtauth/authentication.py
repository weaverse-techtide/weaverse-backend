from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
import jwt
from django.conf import settings
from .models import BlacklistedToken

User = get_user_model()


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        try:
            access_token = auth_header.split(" ")[1]
            payload = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=["HS256"]
            )

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("토큰 만료")
        except IndexError:
            raise AuthenticationFailed("토큰 없음")
        except jwt.DecodeError:
            raise AuthenticationFailed("토큰 오류")

        if BlacklistedToken.objects.filter(token=access_token).exists():
            raise AuthenticationFailed("토큰 사용 불가")

        user = User.objects.filter(id=payload["user_id"]).first()
        if user is None:
            raise AuthenticationFailed("사용자 없음")

        return (user, None)
