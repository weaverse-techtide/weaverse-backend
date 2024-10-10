import pytest
from accounts.admin import CustomUserAdmin
from accounts.models import CustomUser
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory

User = get_user_model()


@pytest.fixture
def admin_site():
    return AdminSite()


@pytest.fixture
def custom_user_admin(admin_site):
    return CustomUserAdmin(CustomUser, admin_site)


@pytest.fixture
def request_factory():
    return RequestFactory()


@pytest.fixture
def admin_user():
    return User.objects.create_superuser("admin@example.com", "adminpassword", "admin")


@pytest.mark.django_db
class TestCustomUserAdmin:
    # Given: CustomUserAdmin이 설정되어 있을 때
    # When: list_display 속성을 확인하면
    # Then: 지정된 필드들이 포함되어 있어야 합니다.
    def test_관리자인터페이스_list_display_확인(self, custom_user_admin):
        assert custom_user_admin.list_display == (
            "email",
            "nickname",
            "is_staff",
            "is_superuser",
        )

    # Given: CustomUserAdmin이 설정되어 있을 때
    # When: ordering 속성을 확인하면
    # Then: 이메일로 정렬되어야 합니다.
    def test_관리자인터페이스_list_정렬_기준_확인(self, custom_user_admin):
        assert custom_user_admin.ordering == (
            "email",
            "created_at",
        )

    # Given: CustomUserAdmin이 설정되어 있을 때
    # When: add_fieldsets 속성을 확인하면
    # Then: 지정된 필드들이 포함되어 있어야 합니다.
    def test_관리자인터페이스_add_fieldsets_속성_확인(self, custom_user_admin):
        fieldsets = custom_user_admin.add_fieldsets[0][1]["fields"]
        assert "email" in fieldsets
        assert "nickname" in fieldsets
        assert "password1" in fieldsets
        assert "password2" in fieldsets
        assert "is_staff" in fieldsets
        assert "is_superuser" in fieldsets

    # Given: 관리자 사용자와 CustomUserAdmin이 설정되어 있을 때
    # When: 일반 사용자를 생성하면
    # Then: create_user 메서드가 호출되어야 합니다.
    def test_관리자인터페이스_save_model_사용자_생성(
        self, custom_user_admin, request_factory, admin_user
    ):
        request = request_factory.post("/admin/accounts/customuser/add/")
        request.user = admin_user
        obj = CustomUser(email="user@example.com", nickname="user")
        form = type(
            "Form",
            (object,),
            {
                "cleaned_data": {
                    "email": "user@example.com",
                    "password1": "userpassword",
                    "nickname": "user",
                    "is_staff": False,
                    "is_superuser": False,
                }
            },
        )()
        custom_user_admin.save_model(request, obj, form, False)
        assert CustomUser.objects.filter(
            email="user@example.com", is_staff=False, is_superuser=False
        ).exists()

    # Given: 관리자 사용자와 CustomUserAdmin이 설정되어 있을 때
    # When: 스태프 사용자를 생성하면
    # Then: create_staff 메서드가 호출되어야 합니다.
    def test_관리자인터페이스_save_model_staff_생성(
        self, custom_user_admin, request_factory, admin_user
    ):
        request = request_factory.post("/admin/accounts/customuser/add/")
        request.user = admin_user
        obj = CustomUser(email="staff@example.com", nickname="staff")
        form = type(
            "Form",
            (object,),
            {
                "cleaned_data": {
                    "email": "staff@example.com",
                    "password1": "staffpassword",
                    "nickname": "staff",
                    "is_staff": True,
                    "is_superuser": False,
                }
            },
        )()
        custom_user_admin.save_model(request, obj, form, False)
        assert CustomUser.objects.filter(
            email="staff@example.com", is_staff=True, is_superuser=False
        ).exists()

    # Given: 관리자 사용자와 CustomUserAdmin이 설정되어 있을 때
    # When: 슈퍼유저를 생성하면
    # Then: create_superuser 메서드가 호출되어야 합니다.
    def test_관리자인터페이스_save_model_superuser_생성(
        self, custom_user_admin, request_factory, admin_user
    ):
        request = request_factory.post("/admin/accounts/customuser/add/")
        request.user = admin_user
        obj = CustomUser(email="super@example.com", nickname="super")
        form = type(
            "Form",
            (object,),
            {
                "cleaned_data": {
                    "email": "super@example.com",
                    "password1": "superpassword",
                    "nickname": "super",
                    "is_staff": True,
                    "is_superuser": True,
                }
            },
        )()
        custom_user_admin.save_model(request, obj, form, False)
        assert CustomUser.objects.filter(
            email="super@example.com", is_staff=True, is_superuser=True
        ).exists()

    # Given: 관리자 사용자와 CustomUserAdmin이 설정되어 있고 기존 사용자가 있을 때
    # When: 기존 사용자를 수정하면
    # Then: 기본 save_model 메서드가 호출되어야 합니다.
    def test_관리자인터페이스_save_model_사용자_갱신(
        self, custom_user_admin, request_factory, admin_user
    ):
        existing_user = CustomUser.objects.create_user(
            "existing@example.com", "password", "existing"
        )
        request = request_factory.post("/admin/accounts/customuser/1/change/")
        request.user = admin_user
        form = type(
            "Form",
            (object,),
            {
                "cleaned_data": {
                    "email": "existing@example.com",
                    "nickname": "updated_nickname",
                }
            },
        )()
        custom_user_admin.save_model(request, existing_user, form, True)
        existing_user.refresh_from_db()
        assert existing_user.nickname == "updated_nickname"
