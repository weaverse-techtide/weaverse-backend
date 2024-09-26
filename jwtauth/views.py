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


class LoginView(APIView):
    """
    사용자 로그인
    접근 권한: 모두
    필수 입력: email, password
    매칭되는 사용자가 있으면 access_token, refresh_token 반환
    매칭이 안되면 401 반환, 회원가입 권유 메시지 출력
    작동 확인: 완료
    """

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
    """
    사용자 로그아웃
    접근 권한: 인증된 사용자
    access_token을 BlacklistedToken에 추가
    응답: 성공시 200 반환, bye 메시지 출력
    """

    # 로그아옷후 토큰 유효성 검사 필요!!
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.auth
        BlacklistedToken.objects.create(token=token)
        return Response({"success": "bye."}, status=status.HTTP_200_OK)


User = get_user_model()


class RefreshTokenView(APIView):
    """
    refresh_token을 받아서 access_token을 재발급
    필수 정보: refresh_token
    refresh_token이 만료되었거나 오류가 있으면 401 반환
    """

    permission_classes = [AllowAny]  # 이전 IsAuthenticated

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response(
                {"error": "리프레시 토큰이 제공되지 않았습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            if BlacklistedToken.objects.filter(token=refresh_token).exists():
                return Response(
                    {"error": "유효하지 않은 리프레시 토큰입니다."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=["HS256"]
            )
            user = CustomUser.objects.get(id=payload["user_id"])

            access_token = generate_access_token(user)
            refresh_token = generate_refresh_token(user)
            return Response(
                {"access_token": access_token, "refresh_token": refresh_token}
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
