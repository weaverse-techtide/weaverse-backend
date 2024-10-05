import pytest
from accounts.models import CustomUser
from accounts.serializers import (CustomUserDetailSerializer,
                                  StudentListSerializer, TutorListSerializer)
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user():
    def _create_user(email, password, nickname, is_staff=False, is_superuser=False):
        return CustomUser.objects.create_user(
            email=email,
            password=password,
            nickname=nickname,
            is_staff=is_staff,
            is_superuser=is_superuser,
        )

    return _create_user


@pytest.mark.django_db
class TestUserRegisterationView:
    # Given: 유효한 사용자 데이터가 주어졌을 때
    # When: 회원가입 요청을 보내면
    # Then: 성공적으로 회원가입이 되어야 합니다.
    def test_user_registration_success(self, api_client):
        url = reverse("accounts:student-register")
        data = {
            "email": "test@example.com",
            "nickname": "testnick",
            "password": "testpassword",
            "confirm_password": "testpassword",
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert "user_id" in response.data
        assert CustomUser.objects.filter(email="test@example.com").exists()

    # Given: 이미 존재하는 이메일로 가입 시도할 때
    # When: 회원가입 요청을 보내면
    # Then: 회원가입이 실패해야 합니다.
    def test_user_registration_duplicate_email(self, api_client, create_user):
        create_user("test@example.com", "password123", "existinguser")
        url = reverse("accounts:student-register")
        data = {
            "email": "test@example.com",
            "nickname": "testnick",
            "password": "testpassword",
            "confirm_password": "testpassword",
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestPasswordResetView:
    # Given: 인증된 사용자가 있을 때
    # When: 비밀번호 재설정 요청을 보내면
    # Then: 비밀번호가 성공적으로 변경되어야 합니다.
    def test_password_reset_success(self, api_client, create_user):
        user = create_user("test@example.com", "CurrentPassword123!", "testnick")
        api_client.force_authenticate(user=user)
        url = reverse("accounts:password-reset")
        data = {
            "current_password": "CurrentPassword123!",
            "new_password": "NewPassword456@",
            "confirm_new_password": "NewPassword456@",
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.check_password("NewPassword456@")

    # Given: 인증되지 않은 사용자일 때
    # When: 비밀번호 재설정 요청을 보내면
    # Then: 권한 오류가 발생해야 합니다.
    def test_password_reset_unauthenticated(self, api_client):
        url = reverse("accounts:password-reset")
        data = {
            "current_password": "currentpassword",
            "new_password": "newpassword",
            "confirm_new_password": "confirmnewpassword",
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestStudentListView:
    # Given: 여러 명의 학생이 존재하고 인증된 사용자가 있을 때
    # When: 학생 목록 조회 요청을 보내면
    # Then: 학생 목록이 정상적으로 반환되어야 합니다.
    def test_student_list_view(self, api_client, create_user):
        create_user("student1@example.com", "password", "student1")
        create_user("student2@example.com", "password", "student2")
        user = create_user("user@example.com", "password", "user")
        api_client.force_authenticate(user=user)
        url = reverse("accounts:student-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3

    # Given: 인증되지 않은 사용자일 때
    # When: 학생 목록 조회 요청을 보내면
    # Then: 권한 오류가 발생해야 합니다.
    def test_student_list_view_unauthenticated(self, api_client):
        url = reverse("accounts:student-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestStudentRetrieveUpdateDestroyView:
    # Given: 학생 사용자가 존재할 때
    # When: 자신의 정보 조회 요청을 보내면
    # Then: 학생 정보가 정상적으로 반환되어야 합니다.
    def test_student_retrieve(self, api_client, create_user):
        student = create_user("student3@example.com", "password", "student")
        api_client.force_authenticate(user=student)
        url = reverse("accounts:student-detail", kwargs={"pk": student.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == "student3@example.com"

    # Given: 학생 사용자가 존재할 때
    # When: 자신의 정보 수정 요청을 보내면
    # Then: 학생 정보가 성공적으로 업데이트되어야 합니다.
    def test_student_update_full(self, api_client, create_user):
        student = create_user("student45@example.com", "OldPassword123!", "student")
        api_client.force_authenticate(user=student)
        url = reverse("accounts:student-detail", kwargs={"pk": student.pk})
        data = {
            "email": "student45@example.com",
            "nickname": "new_nickname",
            "password": "NewPassword456!",
            "confirm_password": "NewPassword456!",
        }
        response = api_client.put(url, data)
        assert response.status_code == status.HTTP_200_OK
        student.refresh_from_db()
        assert student.email == "student45@example.com"
        assert student.nickname == "new_nickname"
        assert student.check_password("NewPassword456!")

    # Given: 학생 사용자가 존재할 때
    # When: 자신의 정보 수정 요청을 보내면
    # Then: 학생 정보가 성공적으로 업데이트되어야 합니다.
    def test_student_update_partial(self, api_client, create_user):
        student = create_user("student5@example.com", "password", "student")
        api_client.force_authenticate(user=student)
        url = reverse("accounts:student-detail", kwargs={"pk": student.pk})
        data = {"nickname": "new_nickname"}
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        student.refresh_from_db()
        assert student.nickname == "new_nickname"

    # Given: 학생 사용자가 존재할 때
    # When: 자신의 계정 삭제 요청을 보내면
    # Then: 계정이 비활성화되어야 합니다.
    def test_student_delete(self, api_client, create_user):
        student = create_user("student@example.com", "password", "student")
        api_client.force_authenticate(user=student)
        url = reverse("accounts:student-detail", kwargs={"pk": student.pk})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        student.refresh_from_db()
        assert not student.is_active


@pytest.mark.django_db
class TestTutorListView:
    # Given: 여러 명의 강사가 존재하고 관리자가 있을 때
    # When: 강사 목록 조회 요청을 보내면
    # Then: 강사 목록이 정상적으로 반환되어야 합니다.
    def test_tutor_list_view(self, api_client, create_user):
        create_user("tutor1@example.com", "password", "tutor1", is_staff=True)
        create_user("tutor2@example.com", "password", "tutor2", is_staff=True)
        admin = create_user(
            "admin@example.com", "password", "admin", is_staff=True, is_superuser=True
        )
        api_client.force_authenticate(user=admin)
        url = reverse("accounts:tutor-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3

    # Given: 일반 사용자일 때
    # When: 강사 목록 조회 요청을 보내면
    # Then: 권한 오류가 발생해야 합니다.
    def test_tutor_list_view_not_admin(self, api_client, create_user):
        user = create_user("user@example.com", "password", "user")
        api_client.force_authenticate(user=user)
        url = reverse("accounts:tutor-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestTutorRetrieveUpdateDestroyView:
    # Given: 강사 사용자가 존재할 때
    # When: 자신의 정보 조회 요청을 보내면
    # Then: 강사 정보가 정상적으로 반환되어야 합니다.
    def test_tutor_retrieve(self, api_client, create_user):
        tutor = create_user("tutor@example.com", "password", "tutor", is_staff=True)
        api_client.force_authenticate(user=tutor)
        url = reverse("accounts:tutor-detail", kwargs={"pk": tutor.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == "tutor@example.com"

    # Given: 강사 사용자가 존재할 때
    # When: 자신의 정보 수정 요청을 보내면
    # Then: 강사 정보가 성공적으로 업데이트되어야 합니다.
    def test_tutor_update_full(self, api_client, create_user):
        tutor = create_user("tutor@example.com", "password", "tutor", is_staff=True)
        api_client.force_authenticate(user=tutor)
        url = reverse("accounts:tutor-detail", kwargs={"pk": tutor.pk})
        data = {
            "email": "tutor@example.com",
            "nickname": "new_nickname",
            "password": "passwordXX123!",
            "confirm_password": "passwordXX123!",
        }
        response = api_client.put(url, data)
        assert response.status_code == status.HTTP_200_OK
        tutor.refresh_from_db()
        assert tutor.nickname == "new_nickname"

    # Given: 강사 사용자가 존재할 때
    # When: 자신의 정보 수정 요청을 보내면
    # Then: 강사 정보가 성공적으로 업데이트되어야 합니다.
    def test_tutor_update_partial(self, api_client, create_user):
        tutor = create_user("tutor@example.com", "password", "tutor", is_staff=True)
        api_client.force_authenticate(user=tutor)
        url = reverse("accounts:tutor-detail", kwargs={"pk": tutor.pk})
        data = {"nickname": "new_nickname"}
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        tutor.refresh_from_db()
        assert tutor.nickname == "new_nickname"

    # Given: 강사 사용자가 존재할 때
    # When: 관리자가 강사 계정 삭제 요청을 보내면
    # Then: 강사 계정이 비활성화되어야 합니다.
    def test_tutor_delete_by_admin(self, api_client, create_user):
        tutor = create_user("tutor@example.com", "password", "tutor", is_staff=True)
        admin = create_user(
            "admin@example.com", "password", "admin", is_staff=True, is_superuser=True
        )
        api_client.force_authenticate(user=admin)
        url = reverse("accounts:tutor-detail", kwargs={"pk": tutor.pk})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        tutor.refresh_from_db()
        assert not tutor.is_active

    # Given: 강사 사용자가 존재할 때
    # When: 다른 강사가 해당 강사의 정보 조회를 시도하면
    # Then: 권한 오류가 발생해야 합니다.
    def test_tutor_retrieve_other_tutor(self, api_client, create_user):
        tutor1 = create_user("tutor1@example.com", "password", "tutor1", is_staff=True)
        tutor2 = create_user("tutor2@example.com", "password", "tutor2", is_staff=True)
        api_client.force_authenticate(user=tutor2)
        url = reverse("accounts:tutor-detail", kwargs={"pk": tutor1.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
