import pytest
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from jwtauth.models import BlacklistedToken
from jwtauth.tasks import delete_expired_tokens
import jwt
from django.conf import settings

User = get_user_model()

@pytest.mark.django_db
def test_만료된_토큰_삭제():
    user = User.objects.create_user(
        email='test1@example.com',
        nickname='testuser1',
        password='testpass'
    )

    now = timezone.now()

    # 만료된 access 토큰 생성
    expired_access_payload = {
        'exp': int(timezone.make_naive(now - timedelta(hours=1)).timestamp())
    }
    expired_access_token = jwt.encode(expired_access_payload, settings.SECRET_KEY, algorithm='HS256')
    BlacklistedToken.objects.create(
        user=user,
        token=expired_access_token,
        token_type="access",
        blacklisted_at=now - timedelta(hours=2)
    )

    # 유효한 access 토큰 생성
    valid_access_payload = {
        'exp': int(timezone.make_naive(now + timedelta(hours=1)).timestamp())
    }
    valid_access_token = jwt.encode(valid_access_payload, settings.SECRET_KEY, algorithm='HS256')
    BlacklistedToken.objects.create(
        user=user,
        token=valid_access_token,
        token_type="access",
        blacklisted_at=now - timedelta(minutes=30)
    )

    # 태스크 실행 전 토큰 수 확인
    assert BlacklistedToken.objects.count() == 2

    # 태스크 실행
    result = delete_expired_tokens()

    # 결과 확인
    assert "1 expired tokens deleted." in result
    assert BlacklistedToken.objects.count() == 1
    assert not BlacklistedToken.objects.filter(token=expired_access_token).exists()
    assert BlacklistedToken.objects.filter(token=valid_access_token).exists()

@pytest.mark.django_db
def test_만료된_토큰이_없는_경우():
    user = User.objects.create_user(
        email='test2@example.com',
        nickname='testuser2',
        password='testpass'
    )

    now = timezone.now()

    # 유효한 access 토큰 생성
    valid_access_payload = {
        'exp': int(timezone.make_naive(now + timedelta(hours=1)).timestamp())
    }
    valid_access_token = jwt.encode(valid_access_payload, settings.SECRET_KEY, algorithm='HS256')
    BlacklistedToken.objects.create(
        user=user,
        token=valid_access_token,
        token_type="access",
        blacklisted_at=now - timedelta(minutes=30)
    )

    # 태스크 실행 전 토큰 수 확인
    assert BlacklistedToken.objects.count() == 1

    # 태스크 실행
    result = delete_expired_tokens()

    # 결과 확인
    assert "0 expired tokens deleted." in result
    assert BlacklistedToken.objects.count() == 1