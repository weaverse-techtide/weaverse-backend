from datetime import timedelta

import jwt
import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import CustomUser as User
from jwtauth.models import BlacklistedToken
from jwtauth.utils.token_generator import generate_access_token, generate_refresh_token


@pytest.fixture
def api_client():
    """
    API 클라이언트를 생성하여 반환합니다.
    """
    client = APIClient()
    client.default_format = "json"
    return client


@pytest.fixture
def user(db):
    """
    테스트용 유저를 생성하여 반환합니다.
    """
    return User.objects.create_user(
        email="test@example.com", password="testpass123", nickname="testuser"
    )


@pytest.fixture
def access_token(user):
    """
    액세스 토큰을 생성하여 반환합니다.
    """
    return generate_access_token(user)


@pytest.fixture
def refresh_token(user):
    """
    리프레시 토큰을 생성하여 반환합니다.
    """
    return generate_refresh_token(user)


@pytest.mark.django_db
def test_로그인_성공(api_client, user):
    """로그인 API를 테스트합니다."""
    # Given: 유효한 사용자 정보가 있음
    # When: 로그인 API에 POST 요청을 보냄
    response = api_client.post(
        reverse("login"), {"email": "test@example.com", "password": "testpass123"}
    )
    # Then: 응답 상태 코드가 200이고, 액세스 토큰과 리프레시 토큰이 포함되어 있음
    assert response.status_code == status.HTTP_302_FOUND
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies


# @pytest.mark.django_db
# def test_로그인_실패(api_client):
#     """로그인 실패 시도를 테스트합니다."""
#     # Given: 잘못된 사용자 정보가 있음
#     # When: 로그인 API에 잘못된 정보로 POST 요청을 보냄
#     response = api_client.post(
#         reverse("login"), {"email": "wrong@example.com", "password": "wrongpass"}
#     )
#     # Then: 응답 상태 코드가 401 (Unauthorized)임
#     assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_로그아웃_성공(api_client, user, refresh_token):
    """로그아웃 API를 테스트합니다."""
    # Given: 인증된 사용자와 유효한 리프레시 토큰이 있음
    api_client.force_authenticate(user=user)
    # When: 로그아웃 API에 리프레시 토큰과 함께 POST 요청을 보냄
    response = api_client.post(reverse("logout"), {"refresh_token": refresh_token})
    # Then: 응답 상태 코드가 200이고, 리프레시 토큰이 블랙리스트에 추가됨
    assert response.status_code == status.HTTP_200_OK
    assert BlacklistedToken.objects.filter(token=refresh_token).exists()


@pytest.mark.django_db
def test_로그아웃_실패_토큰없음(api_client, user):
    """로그아웃 실패 시도를 테스트합니다."""
    # Given: 인증된 사용자가 있지만 리프레시 토큰이 없음
    api_client.force_authenticate(user=user)
    # When: 로그아웃 API에 리프레시 토큰 없이 POST 요청을 보냄
    response = api_client.post(reverse("logout"), {})
    # Then: 응답 상태 코드가 400 (Bad Request)임
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_리프레시_토큰_갱신_성공(api_client, user, refresh_token):
    """리프레시 토큰 갱신 API를 테스트합니다."""
    # Given: 유효한 리프레시 토큰이 있음
    # When: 리프레시 API에 리프레시 토큰과 함께 POST 요청을 보냄
    response = api_client.post(reverse("refresh"), {"refresh_token": refresh_token})
    # Then: 응답 상태 코드가 200이고, 새로운 액세스 토큰과 리프레시 토큰이 반환되며, 기존 리프레시 토큰이 블랙리스트에 추가됨
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.data
    assert "refresh_token" in response.data
    assert BlacklistedToken.objects.filter(token=refresh_token).exists()


@pytest.mark.django_db
def test_리프레시_토큰_갱신_실패_블랙리스트(api_client, user, refresh_token):
    """블랙리스트에 등록된 리프레시 토큰으로 갱신 시도를 테스트합니다."""
    # Given: 블랙리스트에 등록된 리프레시 토큰이 있음
    BlacklistedToken.objects.create(
        token=refresh_token, user=user, token_type="refresh"
    )
    # When: 리프레시 API에 블랙리스트에 등록된 리프레시 토큰과 함께 POST 요청을 보냄
    response = api_client.post(reverse("refresh"), {"refresh_token": refresh_token})
    # Then: 응답 상태 코드가 400 (Bad Request)임
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_JWT_인증_성공(api_client, user, refresh_token):
    """JWT 인증을 테스트합니다."""
    # Given: 유효한 리프레시 토큰이 있음
    url = reverse("refresh")
    # When: 리프레시 API에 유효한 리프레시 토큰과 함께 POST 요청을 보냄
    response = api_client.post(url, {"refresh_token": refresh_token})
    # Then: 응답 상태 코드가 200 (OK)임
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_JWT_인증_실패_만료된_토큰(api_client, user):
    """만료된 토큰으로 JWT 인증 시도를 테스트합니다."""
    # Given: 만료된 토큰이 있음
    payload = {"user_id": user.id, "exp": timezone.now() - timedelta(minutes=1)}
    expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {expired_token}")
    url = reverse("refresh")
    # When: 리프레시 API에 만료된 토큰과 함께 POST 요청을 보냄
    response = api_client.post(url)
    # Then: 응답 상태 코드가 403 (Forbidden)임
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_JWT_인증_실패_유효하지_않은_토큰(api_client):
    """유효하지 않은 토큰으로 JWT 인증 시도를 테스트합니다."""
    # Given: 유효하지 않은 토큰이 있음
    api_client.credentials(HTTP_AUTHORIZATION="Bearer invalidtoken")
    url = reverse("refresh")
    # When: 리프레시 API에 유효하지 않은 토큰과 함께 POST 요청을 보냄
    response = api_client.post(url)
    # Then: 응답 상태 코드가 403 (Forbidden)임
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_액세스_토큰_생성(user):
    """액세스 토큰을 생성하는 함수를 테스트합니다."""
    # Given: 유효한 사용자가 있음
    # When: 액세스 토큰을 생성함
    token = generate_access_token(user)
    # Then: 생성된 토큰이 유효하고 사용자 ID와 만료 시간을 포함함
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    assert payload["user_id"] == user.id
    assert "exp" in payload


@pytest.mark.django_db
def test_리프레시_토큰_생성(user):
    """리프레시 토큰을 생성하는 함수를 테스트합니다."""
    # Given: 유효한 사용자가 있음
    # When: 리프레시 토큰을 생성함
    token = generate_refresh_token(user)
    # Then: 생성된 토큰이 유효하고 사용자 ID와 만료 시간을 포함함
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    assert payload["user_id"] == user.id
    assert "exp" in payload
