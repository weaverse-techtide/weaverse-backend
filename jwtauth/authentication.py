from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
import jwt, logging
from django.conf import settings


logger = logging.getLogger(__name__)
User = get_user_model()


class JWTAuthentication(BaseAuthentication):
    """
    해당 클래스는 JWT 토큰을 사용하여 사용자를 인증하는 데 사용됩니다.
    - 토큰이 유효하지 않으면 해당하는 메시지를 반환합니다.
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

            user = User(
                id=payload["user_id"],
                email=payload.get("email"),
                is_staff=payload.get("is_staff"),
                is_superuser=payload.get("is_superuser"),
            )
            user.is_authenticated = True

            return (user, None)

        except jwt.ExpiredSignatureError: 
            raise AuthenticationFailed("토큰이 만료되었습니다!")
        except IndexError: 
            raise AuthenticationFailed("토큰이 없습니다!")
        except jwt.DecodeError: 
            raise AuthenticationFailed("토큰이 유효하지 않습니다!")
        except Exception as e: #
            logger.error(f"인증 오류: {str(e)}")
            raise AuthenticationFailed(f"인증이 유효하지 않습니다!")

    def authenticate_header(self, request):
        return "Bearer"
