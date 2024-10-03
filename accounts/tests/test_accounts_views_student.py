import pytest
from accounts.models import CustomUser
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestStudentListCreateView:
    def setup_method(self, method):
        self.client = APIClient()

    def test_list_students(self):
        CustomUser.objects.create_user(
            email="student1@example.com", password="pass123", is_staff=False
        )
        CustomUser.objects.create_user(
            email="student2@example.com", password="pass123", is_staff=False
        )

        response = self.client.get("/api/students/")
        assert response.status_code == 200
        assert len(response.data["results"]) == 2

    def test_create_student(self):
        data = {
            "email": "newstudent@example.com",
            "password": "NewPass123!",
            "confirm_password": "NewPass123!",
            "nickname": "NewStudent",
        }
        response = self.client.post("/api/students/", data)
        assert response.status_code == 201
        assert CustomUser.objects.filter(email="newstudent@example.com").exists()


@pytest.mark.django_db
class TestStudentRetrieveUpdateDestroyView:
    def setup_method(self, method):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            email="student@example.com", password="pass123", is_staff=False
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_student(self):
        response = self.client.get(f"/api/students/{self.user.id}/")
        assert response.status_code == 200
        assert response.data["email"] == "student@example.com"

    def test_update_student(self):
        data = {"nickname": "UpdatedNickname"}
        response = self.client.put(f"/api/students/{self.user.id}/", data)
        assert response.status_code == 200
        assert response.data["nickname"] == "UpdatedNickname"

    def test_delete_student(self):
        response = self.client.delete(f"/api/students/{self.user.id}/")
        assert response.status_code == 204
        self.user.refresh_from_db()
        assert not self.user.is_active
