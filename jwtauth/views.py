from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.contrib.auth import authenticate, get_user_model
from django.conf import settings
from .serializers import (
    LoginSerializer,
    LogoutSerializer,
    RefreshTokenSerializer,
)
from .utils.token_generator import (
    generate_access_token,
    generate_refresh_token,
)
from .models import BlacklistedToken
import jwt, logging


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
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.GOOGLE_CALLBACK_URL
    client_class = OAuth2Client

    def get_response(self):
        response = super().get_response()
        user = self.user
        access_token = generate_access_token(user)
        refresh_token = generate_refresh_token(user)

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="None",
        )
        response.data = {"access_token": access_token}

        return response
