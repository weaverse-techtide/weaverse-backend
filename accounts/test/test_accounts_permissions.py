import pytest
from accounts.permissions import IsAuthenticatedAndActive, IsSuperUser, IsTutor
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

User = get_user_model()


@pytest.fixture
def api_request_factory():
    return APIRequestFactory()


@pytest.fixture
def mock_view():
    return APIView()


@pytest.fixture
def create_user():
    def _create_user(
        email, password, nickname, is_active=True, is_staff=False, is_superuser=False
    ):
        return User.objects.create_user(
            email=email,
            password=password,
            nickname=nickname,
            is_active=is_active,
            is_staff=is_staff,
            is_superuser=is_superuser,
        )

    return _create_user


@pytest.mark.django_db
class TestIsAuthenticatedAndActive:
    # Given: 인증되고 활성화된 사용자가 있을 때
    # When: IsAuthenticatedAndActive 권한을 검사하면
    # Then: 권한이 허용되어야 합니다.
    def test_authenticated_그리고_active_user_확인(
        self, api_request_factory, mock_view, create_user
    ):
        user = create_user("user@example.com", "password", "nickname", is_active=True)
        request = api_request_factory.get("/")
        request.user = user
        permission = IsAuthenticatedAndActive()
        assert permission.has_permission(request, mock_view) is True

    # Given: 인증되었지만 비활성화된 사용자가 있을 때
    # When: IsAuthenticatedAndActive 권한을 검사하면
    # Then: 권한이 거부되어야 합니다.
    def test_authenticated_그러나_inactive_user_확인(
        self, api_request_factory, mock_view, create_user
    ):
        user = create_user("user@example.com", "password", "nickname", is_active=False)
        request = api_request_factory.get("/")
        request.user = user
        permission = IsAuthenticatedAndActive()
        assert permission.has_permission(request, mock_view) is False

    # Given: 인증되지 않은 사용자가 있을 때
    # When: IsAuthenticatedAndActive 권한을 검사하면
    # Then: 권한이 거부되어야 합니다.
    def test_비_authenticated_user_확인(self, api_request_factory, mock_view):
        request = api_request_factory.get("/")
        request.user = None
        permission = IsAuthenticatedAndActive()
        assert permission.has_permission(request, mock_view) is False


@pytest.mark.django_db
class TestIsTutor:
    # Given: 인증되고 활성화된 강사 사용자가 있을 때
    # When: IsTutor 권한을 검사하면
    # Then: 권한이 허용되어야 합니다.
    def test_authenticated_active_tutor임을_확인(
        self, api_request_factory, mock_view, create_user
    ):
        user = create_user(
            "tutor@example.com", "password", "nickname", is_active=True, is_staff=True
        )
        request = api_request_factory.get("/")
        request.user = user
        permission = IsTutor()
        assert permission.has_permission(request, mock_view) is True

    # Given: 인증되고 활성화되었지만 강사가 아닌 사용자가 있을 때
    # When: IsTutor 권한을 검사하면
    # Then: 권한이 거부되어야 합니다.
    def test_authenticated_active_그러나_non_tutor임을_확인(
        self, api_request_factory, mock_view, create_user
    ):
        user = create_user(
            "user@example.com", "password", "nickname", is_active=True, is_staff=False
        )
        request = api_request_factory.get("/")
        request.user = user
        permission = IsTutor()
        assert permission.has_permission(request, mock_view) is False

    # Given: 인증되지 않은 사용자가 있을 때
    # When: IsTutor 권한을 검사하면
    # Then: 권한이 거부되어야 합니다.
    def test_비_authenticated_user_일때_tutor_검사_거부(
        self, api_request_factory, mock_view
    ):
        request = api_request_factory.get("/")
        request.user = None
        permission = IsTutor()
        assert permission.has_permission(request, mock_view) is False


@pytest.mark.django_db
class TestIsSuperUser:
    # Given: 인증되고 활성화된 관리자 사용자가 있을 때
    # When: IsSuperUser 권한을 검사하면
    # Then: 권한이 허용되어야 합니다.
    def test_authenticated_active_superuser임을_확인(
        self, api_request_factory, mock_view, create_user
    ):
        user = create_user(
            "admin@example.com",
            "password",
            "nickname",
            is_active=True,
            is_superuser=True,
        )
        request = api_request_factory.get("/")
        request.user = user
        permission = IsSuperUser()
        assert permission.has_permission(request, mock_view) is True

    # Given: 인증되고 활성화되었지만 관리자가 아닌 사용자가 있을 때
    # When: IsSuperUser 권한을 검사하면
    # Then: 권한이 거부되어야 합니다.
    def test_authenticated_active_그러나_non_superuser임을_확인(
        self, api_request_factory, mock_view, create_user
    ):
        user = create_user(
            "user@example.com",
            "password",
            "nickname",
            is_active=True,
            is_superuser=False,
        )
        request = api_request_factory.get("/")
        request.user = user
        permission = IsSuperUser()
        assert permission.has_permission(request, mock_view) is False

    # Given: 인증되지 않은 사용자가 있을 때
    # When: IsSuperUser 권한을 검사하면
    # Then: 권한이 거부되어야 합니다.
    def test_비_authenticated_user_일때_superuser_검사_거부(
        self, api_request_factory, mock_view
    ):
        request = api_request_factory.get("/")
        request.user = None
        permission = IsSuperUser()
        assert permission.has_permission(request, mock_view) is False
