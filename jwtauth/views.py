from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from .serializers import (
    LoginSerializer,
    LogoutSerializer,
    RefreshTokenSerializer,
    SocialLoginSerializer,
)
from .utils.token_generator import (
    generate_access_token,
    generate_refresh_token,
)
from .utils.send_welcome_email import send_welcome_email
from .models import BlacklistedToken
import jwt, logging
from social_django.utils import load_strategy, load_backend
from social_core.exceptions import MissingBackend, AuthTokenError, AuthForbidden
from requests.exceptions import HTTPError
from .models import SocialAccount
from accounts.models import CustomUser


logger = logging.getLogger(__name__)


class LoginView(GenericAPIView):
    """
    사용자가 로그인할 때 사용, email과 password를 받아서 인증 합니다.
    email과 password가 일치하고 활성화된 사용자인 경우, access,refresh 토큰을 반환합니다.
    """

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            user = authenticate(email=email, password=password)

            if user is not None and user.is_active:
                access_token = generate_access_token(user)
                refresh_token = generate_refresh_token(user)

                response = Response({"access_token": access_token})
                response.set_cookie(
                    key="refresh_token",
                    value=refresh_token,
                    httponly=True,
                    secure=not settings.DEBUG,
                    samesite="None",
                )
                return response
            else:
                return Response(
                    {"error": "회원 가입하세요"}, status=status.HTTP_401_UNAUTHORIZED
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(GenericAPIView):
    """
    사용자가 로그아웃할 때 사용, 현재 refresh 토큰을 블랙리스트에 추가합니다.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request):

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            refresh_token = serializer.validated_data["refresh_token"]

            try:
                BlacklistedToken.objects.create(
                    token=refresh_token, user=request.user, token_type="refresh"
                )
                return Response(
                    {"success": "로그아웃 완료."},
                    status=status.HTTP_200_OK,
                )

            except Exception as e:
                logger.error(f"블랙리스트에 추가하는 중 오류 발생: {str(e)}")
                return Response(
                    {"error": "로그아웃 중 오류 발생."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RefreshTokenView(GenericAPIView):
    """
    사용자가 리프레시 토큰을 제공하면 새로운 액세스, 리프레시 토큰을 반환합니다.
    사용된 리프레시 토큰은 블랙리스트에 추가됩니다.
    """

    permission_classes = [AllowAny]
    serializer_class = RefreshTokenSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            refresh_token = serializer.validated_data["refresh_token"]

            try:
                payload = jwt.decode(
                    refresh_token, settings.SECRET_KEY, algorithms=["HS256"]
                )
                user = CustomUser.objects.get(id=payload["user_id"])

                if not user.is_active:
                    return Response(
                        {"error": "비활성화된 유저입니다."},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )

                access_token = generate_access_token(user)
                new_refresh_token = generate_refresh_token(user)

                BlacklistedToken.objects.create(
                    token=refresh_token, user=user, token_type="refresh"
                )
                return Response(
                    {"access_token": access_token, "refresh_token": new_refresh_token},
                    status=status.HTTP_200_OK,
                )

            except jwt.ExpiredSignatureError:
                return Response(
                    {"error": "인증 요청이 유효하지 않습니다."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            except (jwt.DecodeError, CustomUser.DoesNotExist):
                return Response(
                    {"error": "인증 요청이 유효하지 않습니다."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            except Exception as e:
                logger.error(f"토큰 갱신 중 오류 발생: {str(e)}")
                return Response(
                    {"error": "인증 중 오류 발생, 나중에 다시 시도해주세요."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SocialLoginView(GenericAPIView):
    """
    사용자가 소셜 로그인할 때 사용, 소셜 로그인을 통해 인증하고 access, refresh 토큰을 반환합니다.
    가입되지 않은 사용자는 자동으로 가입되며, 이미 가입된 사용자는 로그인합니다.
    uid와 provider가 일치하면 기존 사용자와 연결합니다.
    """

    serializer_class = SocialLoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        provider = serializer.validated_data["provider"]
        access_token = serializer.validated_data["access_token"]

        try:
            strategy = load_strategy(request)
            backend = load_backend(strategy=strategy, name=provider, redirect_uri=None)

            user = backend.do_auth(access_token)

            if user:
                if not user.is_active:
                    return Response(
                        {"error": "비활성화된 유저입니다."},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                response = backend.user_data(access_token)

                uid = response.get("sub")
                if not uid:
                    return Response(
                        {"error": "유효한 사용자 데이터를 가져오지 못했습니다."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                social_account, created = SocialAccount.objects.update_or_create(
                    provider=provider, uid=uid, defaults={"user": user}
                )
                if created:
                    send_welcome_email(user)

                access_token = generate_access_token(user)
                refresh_token = generate_refresh_token(user)

                response = Response(
                    {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "user": {
                            "id": user.id,
                            "email": user.email,
                            "nickname": user.nickname,
                        },
                    },
                    status=status.HTTP_200_OK,
                )
                response.set_cookie(
                    key="refresh_token",
                    value=refresh_token,
                    httponly=True,
                    secure=settings.DEBUG,
                    samesite="None",
                )
                return response

        except (MissingBackend, AuthTokenError, AuthForbidden, HTTPError) as e:
            logger.error(f"소셜 로그인 중 오류 발생: {str(e)}")
            return Response(
                {"error": "유효하지 않은 사용자입니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )
