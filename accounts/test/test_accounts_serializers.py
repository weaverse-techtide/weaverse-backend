import pytest
from django.contrib.auth import get_user_model

from accounts.serializers import (
    CustomUserDetailSerializer,
    PasswordResetSerializer,
    StudentListSerializer,
    TutorListSerializer,
    UserRegistrationSerializer,
)

User = get_user_model()


@pytest.mark.django_db
class TestUserRegistrationSerializer:
    # Given: 유효한 사용자 데이터가 주어졌을 때
    # When: UserRegistrationSerializer를 통해 데이터를 검증하면
    # Then: 데이터가 유효해야 합니다.
    def test_valid_user_data(self):
        data = {
            "email": "test@example.com",
            "password": "StrongPass1!",
            "confirm_password": "StrongPass1!",
            "nickname": "testuser",
        }
        serializer = UserRegistrationSerializer(data=data)
        assert serializer.is_valid()

    # Given: 이미 존재하는 이메일로 데이터가 주어졌을 때
    # When: UserRegistrationSerializer를 통해 데이터를 검증하면
    # Then: 유효성 검사에 실패해야 합니다.
    def test_duplicate_email(self):
        User.objects.create_user(
            email="existing@example.com", password="password", nickname="existing"
        )
        data = {
            "email": "existing@example.com",
            "password": "NewPass1!",
            "nickname": "newuser",
        }
        serializer = UserRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors


@pytest.mark.django_db
class TestPasswordResetSerializer:
    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            email="test@example.com", password="OldPass1!", nickname="testuser"
        )

    # Given: 유효한 비밀번호 재설정 데이터가 주어졌을 때
    # When: PasswordResetSerializer를 통해 데이터를 검증하면
    # Then: 데이터가 유효해야 합니다.
    def test_valid_password_reset(self, user, rf):
        request = rf.get("/")
        request.user = user
        data = {
            "current_password": "OldPass1!",
            "new_password": "NewStrongPass2@",
            "confirm_new_password": "NewStrongPass2@",
        }
        serializer = PasswordResetSerializer(data=data, context={"request": request})
        assert serializer.is_valid()

    # Given: 현재 비밀번호가 틀린 데이터가 주어졌을 때
    # When: PasswordResetSerializer를 통해 데이터를 검증하면
    # Then: 유효성 검사에 실패해야 합니다.
    def test_invalid_current_password(self, user, rf):
        request = rf.get("/")
        request.user = user
        data = {
            "current_password": "WrongPass1!",
            "new_password": "NewStrongPass2@",
            "confirm_new_password": "NewStrongPass2@",
        }
        serializer = PasswordResetSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "current_password" in serializer.errors

    # Given: 새 비밀번호가 복잡성 요구사항을 충족하지 않을 때
    # When: PasswordResetSerializer를 통해 데이터를 검증하면
    # Then: 유효성 검사에 실패해야 합니다.
    def test_weak_new_password(self, user, rf):
        request = rf.get("/")
        request.user = user
        data = {
            "current_password": "OldPass1!",
            "new_password": "weak",
            "confirm_new_password": "weak",
        }
        serializer = PasswordResetSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "new_password" in serializer.errors


@pytest.mark.django_db
class TestStudentListSerializer:
    # Given: 학생 사용자가 있을 때
    # When: StudentListSerializer를 사용해 직렬화하면
    # Then: 지정된 필드만 포함되어야 합니다.
    def test_student_serialization(self):
        student = User.objects.create_user(
            email="student@example.com", password="Pass1!", nickname="student"
        )
        serializer = StudentListSerializer(student)
        assert set(serializer.data.keys()) == {"id", "email", "nickname", "created_at"}


@pytest.mark.django_db
class TestTutorListSerializer:
    # Given: 강사 사용자가 있을 때
    # When: TutorListSerializer를 사용해 직렬화하면
    # Then: 지정된 필드만 포함되어야 합니다.
    def test_tutor_serialization(self):
        tutor = User.objects.create_user(
            email="tutor@example.com",
            password="Pass1!",
            nickname="tutor",
            is_staff=True,
        )
        serializer = TutorListSerializer(tutor)
        assert set(serializer.data.keys()) == {"id", "email", "nickname", "created_at"}


@pytest.mark.django_db
class TestCustomUserDetailSerializer:
    @pytest.fixture
    def student(self):
        return User.objects.create_user(
            email="student@example.com", password="Pass1!", nickname="student"
        )

    @pytest.fixture
    def tutor(self):
        return User.objects.create_user(
            email="tutor@example.com",
            password="Pass1!",
            nickname="tutor",
            is_staff=True,
        )

    @pytest.fixture
    def admin(self):
        return User.objects.create_superuser(
            email="admin@example.com", password="Pass1!", nickname="admin"
        )

    # Given: 학생 사용자가 있을 때
    # When: CustomUserDetailSerializer를 사용해 직렬화하면
    # Then: 학생에 해당하는 필드만 포함되어야 합니다.
    def test_student_serialization(self, student):
        serializer = CustomUserDetailSerializer(student)
        assert "user_type" in serializer.data
        assert serializer.data["user_type"] == "student"
        assert "student_count" not in serializer.data
        assert "tutor_count" not in serializer.data

    # Given: 강사 사용자가 있을 때
    # When: CustomUserDetailSerializer를 사용해 직렬화하면
    # Then: 강사에 해당하는 필드만 포함되어야 합니다.
    def test_tutor_serialization(self, tutor):
        serializer = CustomUserDetailSerializer(tutor)
        assert "user_type" in serializer.data
        assert serializer.data["user_type"] == "tutor"
        assert "student_count" in serializer.data
        assert "tutor_count" not in serializer.data

    # Given: 관리자 사용자가 있을 때
    # When: CustomUserDetailSerializer를 사용해 직렬화하면
    # Then: 관리자에 해당하는 모든 필드가 포함되어야 합니다.
    def test_admin_serialization(self, admin):
        serializer = CustomUserDetailSerializer(admin)
        assert "user_type" in serializer.data
        assert serializer.data["user_type"] == "superuser"
        assert "student_count" in serializer.data
        assert "tutor_count" in serializer.data

    # Given: 유효한 사용자 데이터가 주어졌을 때
    # When: CustomUserDetailSerializer를 통해 데이터를 검증하면
    # Then: 데이터가 유효해야 합니다.
    def test_valid_user_data(self):
        data = {
            "email": "new@example.com",
            "password": "NewPass1!",
            "confirm_password": "NewPass1!",
            "nickname": "newuser",
        }
        serializer = CustomUserDetailSerializer(data=data)
        assert serializer.is_valid()

    # Given: 비밀번호와 확인 비밀번호가 일치하지 않는 데이터가 주어졌을 때
    # When: CustomUserDetailSerializer를 통해 데이터를 검증하면
    # Then: 유효성 검사에 실패해야 합니다.
    def test_password_mismatch(self):
        data = {
            "email": "new@example.com",
            "password": "NewPass1!",
            "confirm_password": "DifferentPass1!",
            "nickname": "newuser",
        }
        serializer = CustomUserDetailSerializer(data=data)
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors

    # Given: 약한 비밀번호가 포함된 데이터가 주어졌을 때
    # When: CustomUserDetailSerializer를 통해 데이터를 검증하면
    # Then: 유효성 검사에 실패해야 합니다.
    def test_weak_password(self):
        data = {
            "email": "new@example.com",
            "password": "weak",
            "confirm_password": "weak",
            "nickname": "newuser",
        }
        serializer = CustomUserDetailSerializer(data=data)
        assert not serializer.is_valid()
        assert "password" in serializer.errors
