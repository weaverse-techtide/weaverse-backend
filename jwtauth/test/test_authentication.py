from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from jwtauth.models import BlacklistedToken
from jwtauth.utils import generate_access_token, generate_refresh_token
from jwtauth.authentication import JWTAuthentication
import jwt
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()


class JWTAuthenticationTest(TestCase):
    """
    인증 관련 테스트 케이스
    """

    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()
        self.login_url = reverse("login")
        self.logout_url = reverse("logout")
        self.refresh_url = reverse("refresh")
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpass123", is_active=True
        )
        self.jwt_auth = JWTAuthentication()

    def test_login_success(self):
        """
        - 올바른 이메일과 비밀번호로 로그인 성공을 확인
        - 응답에 access_token과 refresh_token이 포함되어 있는지 확인
        """
        response = self.client.post(
            self.login_url,
            {"email": "testuser@example.com", "password": "testpass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)
        self.assertIn("refresh_token", response.data)

    def test_login_fail(self):
        """
        - 잘못된 비밀번호로 로그인 실패를 확인
        """
        response = self.client.post(
            self.login_url,
            {"email": "testuser@example.com", "password": "wrongpass"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout(self):
        """
        - 로그아웃 과정을 테스트
        - 로그아웃 후 refresh 토큰이 블랙리스트에 추가되었는지 확인
        """
        access_token = generate_access_token(self.user)
        refresh_token = generate_refresh_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.post(
            self.logout_url, {"refresh_token": refresh_token}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(BlacklistedToken.objects.filter(token=refresh_token).exists())

    def test_refresh_token(self):
        """
        - 새로운 access_token과 refresh_token을 받는 과정을 테스트
        - 이전 refresh 토큰이 블랙리스트에 추가되었는지 확인
        """
        refresh_token = generate_refresh_token(self.user)
        response = self.client.post(
            self.refresh_url, {"refresh_token": refresh_token}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)
        self.assertIn("refresh_token", response.data)
        self.assertTrue(BlacklistedToken.objects.filter(token=refresh_token).exists())

    def test_refresh_token_blacklisted(self):
        """
        - 이미 블랙리스트에 있는 refresh 토큰으로 요청 시 실패하는지 확인
        """
        refresh_token = generate_refresh_token(self.user)
        BlacklistedToken.objects.create(
            token=refresh_token, user=self.user, token_type="refresh"
        )
        response = self.client.post(
            self.refresh_url, {"refresh_token": refresh_token}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_expired(self):
        """
        - 만료된 refresh 토큰으로 요청 시 실패하는지 확인
        """
        payload = {
            "user_id": self.user.id,
            "exp": timezone.now() - timedelta(minutes=1),
        }
        expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        response = self.client.post(
            self.refresh_url, {"refresh_token": expired_token}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authentication_success(self):
        """
        - 유효한 access 토큰으로 인증이 성공하는지 확인

        """
        access_token = generate_access_token(self.user)
        request = self.factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"
        user_info, _ = self.jwt_auth.authenticate(request)
        self.assertIsNotNone(user_info)
        self.assertEqual(user_info.id, self.user.id)

    def test_authentication_fail_invalid_token(self):
        """
        - 유효하지 않은 토큰으로 인증 시 실패하는지 확인
        """
        request = self.factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = "Bearer invalidtoken"
        with self.assertRaises(AuthenticationFailed):
            self.jwt_auth.authenticate(request)

    def test_authentication_fail_expired_token(self):
        """
        - 만료된 access 토큰으로 인증 시 실패하는지 확인
        """
        payload = {
            "user_id": self.user.id,
            "is_staff": self.user.is_staff,
            "is_superuser": self.user.is_superuser,
            "exp": timezone.now() - timedelta(minutes=1),
        }
        expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        request = self.factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = f"Bearer {expired_token}"
        with self.assertRaises(AuthenticationFailed):
            self.jwt_auth.authenticate(request)

    def test_authentication_no_token(self):
        """
        - 토큰이 없는 경우 인증 결과가 None인지 확인
        """
        request = self.factory.get("/")
        result = self.jwt_auth.authenticate(request)
        self.assertIsNone(result)
