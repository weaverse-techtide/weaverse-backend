from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
import jwt, logging
from django.core.cache import cache
from django.conf import settings


logger = logging.getLogger(__name__)
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

            user_id = payload["user_id"]

            cache_key = f"user_{user_id}"
            user_data = cache.get(cache_key)

            if user_data is None:
                user = User.objects.get(id=user_id)
                user_data = {
                    "id": user.id,
                    "email": user.email,
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                }
                cache.set(cache_key, user_data, timeout=18000)

            user = User(
                id=user_data["id"],
                email=user_data["email"],
                is_staff=user_data["is_staff"],
                is_superuser=user_data["is_superuser"],
            )

            return (user, None)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("토큰이 만료되었습니다!")
        except IndexError:
            raise AuthenticationFailed("토큰이 없습니다!")
        except jwt.DecodeError:
            raise AuthenticationFailed("토큰이 유효하지 않습니다!")
        except User.DoesNotExist:
            raise AuthenticationFailed("유효하지 않은 사용자입니다!")
        except Exception as e:
            logger.error(f"인증 오류: {str(e)}")
            raise AuthenticationFailed("인증이 유효하지 않습니다!")
