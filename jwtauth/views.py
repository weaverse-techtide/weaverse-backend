from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, get_user_model
from django.conf import settings
from .utils import generate_access_token, generate_refresh_token
from .models import BlacklistedToken
from rest_framework.permissions import IsAuthenticated, AllowAny
import jwt


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(email=email, password=password)

        if user is not None:
            access_token = generate_access_token(user)
            refresh_token = generate_refresh_token(user)

            return Response(
                {"access_token": access_token, "refresh_token": refresh_token}
            )
        else:
            return Response(
                {"error": "회원 가입하세요"}, status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.auth
        BlacklistedToken.objects.create(token=token)
        return Response({"success": "bye."}, status=status.HTTP_200_OK)


User = get_user_model()


class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response(
                {"error": "인증이 만료되었습니다, 다시 로그인하세요."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=["HS256"]
            )
            user = User.objects.get(id=payload["user_id"])
            access_token = generate_access_token(user)
            return Response({"access_token": access_token})
        except jwt.ExpiredSignatureError:
            return Response({"error": "인증 만료"}, status=status.HTTP_401_UNAUTHORIZED)
        except (jwt.DecodeError, User.DoesNotExist):
            return Response({"error": "토큰 오류"}, status=status.HTTP_401_UNAUTHORIZED)
