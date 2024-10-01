from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, get_user_model
from django.conf import settings
from .utils import generate_access_token, generate_refresh_token
from .models import BlacklistedToken
from rest_framework.permissions import IsAuthenticated, AllowAny
import jwt
from accounts.models import CustomUser
from .serializers import LoginSerializer, LogoutSerializer, RefreshTokenSerializer
from rest_framework.generics import GenericAPIView


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

                return Response(
                    {"access_token": access_token, "refresh_token": refresh_token}
                )

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
                BlacklistedToken.objects.create(token=refresh_token, user=request.user)
                return Response(
                    {
                        "success": "로그아웃 완료. refresh 토큰이 블랙리스트에 추가되었습니다."
                    },
                    status=status.HTTP_200_OK,
                )

            except Exception as e:
                return Response(
                    {"error": f"블랙리스트에 추가하는 중 오류 발생: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


User = get_user_model()


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
                    {"error": "리프레시 토큰이 만료되었습니다."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            except (jwt.DecodeError, User.DoesNotExist):
                return Response(
                    {"error": "유효하지 않은 리프레시 토큰입니다."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            except Exception as e:
                return Response(
                    {"error": f"토큰 갱신 중 오류 발생: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
