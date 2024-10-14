import logging
import jwt
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import BlacklistedToken
from .serializers import LoginSerializer, LogoutSerializer, RefreshTokenSerializer
from .utils.token_generator import generate_access_token, generate_refresh_token

logger = logging.getLogger(__name__)
User = get_user_model()


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

                response = redirect(settings.LOGIN_REDIRECT_URL)
                same_site = None if settings.DEBUG else "Lax"
                response.set_cookie(
                    key="refresh_token",
                    value=refresh_token,
                    httponly=True,
                    secure=not settings.DEBUG,
                    samesite=same_site,
                    max_age=60 * 60 * 24 * 14,
                )
                response.set_cookie(
                    key="access_token",
                    value=access_token,
                    secure=not settings.DEBUG,
                    samesite=same_site,
                    max_age=60 * 30,
                )
                return response
            else:
                return redirect(settings.SIGNUP_REDIRECT_URL)
        else:
            return redirect(settings.SIGNUP_REDIRECT_URL)


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
                user = User.objects.get(id=payload["user_id"])

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
            except (jwt.DecodeError, User.DoesNotExist):
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


class GoogleLogin(SocialLoginView):
    """
    사용자가 구글 로그인을 할 때 사용, 구글 로그인을 위한 소셜 로그인 뷰입니다.
    사용자가 구글사이트에서 로그인을 완료하면, 사용자 정보를 받아서 회원가입 또는 로그인 처리합니다.
    닉네임은 이메일 주소의 @ 앞부분을 사용하고, 비밀번호는 사용하지 않습니다.
    쿠기에 리프레시 토큰과 액세스 토큰을 저장합니다.
    """

    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.GOOGLE_CALLBACK_URL
    client_class = OAuth2Client

    def get_response(self):
        """
        소셜 로그인 완료 후 사용자 정보 처리
        """
        response = super().get_response()

        user = self.user

        if not User.objects.filter(email=user.email).exists():
            user = User.objects.create_user(
                nickname=user.email.split("@")[0],
                email=user.email,
            )
            user.set_unusable_password()
            user.save()

        access_token = generate_access_token(user)
        refresh_token = generate_refresh_token(user)

        response = redirect(settings.LOGIN_REDIRECT_URL)
        same_site = None if settings.DEBUG else "Lax"
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite=same_site,
            max_age=60 * 60 * 24 * 14,
        )
        response.set_cookie(
            key="access_token",
            value=access_token,
            secure=not settings.DEBUG,
            samesite=same_site,
            max_age=60 * 30,
        )
        return response
