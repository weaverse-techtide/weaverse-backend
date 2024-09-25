from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
import jwt
from django.conf import settings
from .models import BlacklistedToken

TOKEN_EXPIRED = "사용자 혹은 토큰이 유효하지 않습니다!"

# CustomUser 모델 직접 임포트 대신 get_user_model() 사용
User = get_user_model()


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

            # 관리자가 특정 access토큰을 블랙리스트에 추가할 필요있을까?
            # if BlacklistedToken.objects.filter(token=access_token).exists():
            #     raise AuthenticationFailed("토큰이 블랙리스트에 등록되었습니다!")

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
