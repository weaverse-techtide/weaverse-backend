from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
import jwt
from django.conf import settings

# from .models import BlacklistedToken 상의 필요

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

            user_id = payload.get("user_id")
            if user_id is None:
                raise AuthenticationFailed("유효하지 않은 페이로드입니다!")

            user = User.objects.filter(id=user_id).first()
            if user is None:
                raise AuthenticationFailed("사용자를 찾을 수 없습니다!")

            return (user, None)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("토큰이 만료되었습니다!")
        except IndexError:
            raise AuthenticationFailed("토큰이 유효하지 않습니다!")
        except jwt.DecodeError:
            raise AuthenticationFailed("토큰 디코딩 오류!")
        except Exception as e:
            raise AuthenticationFailed(f"인증 오류: {str(e)}")

    def authenticate_header(self, request):
        return "Bearer"
