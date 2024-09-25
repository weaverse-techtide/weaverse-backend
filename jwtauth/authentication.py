from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
import jwt
from django.conf import settings
from .models import BlacklistedToken
from .models import CustomUser

TOKEN_EXPIRED = "사용자 혹은 토큰이 유효하지 않습니다!"


class JWTAuthentication(BaseAuthentication):
    """
    사용자 인증
    헤더에 Authorization: Bearer <access_token>을 포함하여 요청
    access_token이 만료되었거나 없거나 오류가 있으면 401 반환
    access_token이 BlacklistedToken에 있으면 401 반환
    access_token이 유효하면 사용자 반환
    """

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
            raise AuthenticationFailed(TOKEN_EXPIRED)
        except IndexError:
            raise AuthenticationFailed(TOKEN_EXPIRED)
        except jwt.DecodeError:
            raise AuthenticationFailed(TOKEN_EXPIRED)

        if BlacklistedToken.objects.filter(token=access_token).exists():
            raise AuthenticationFailed(TOKEN_EXPIRED)

        user = CustomUser.objects.filter(id=payload["user_id"]).first()
        if user is None:
            raise AuthenticationFailed(TOKEN_EXPIRED)

        return (user, None)
