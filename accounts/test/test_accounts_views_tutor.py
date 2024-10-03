import pytest
from accounts.models import CustomUser
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestTutorStudentView:
    def setup_method(self, method):
        self.client = APIClient()
        self.tutor = CustomUser.objects.create_user(
            email="tutor@example.com", password="pass123", is_staff=True
        )
        self.student1 = CustomUser.objects.create_user(
            email="student1@example.com", password="pass123", is_staff=False
        )
        self.student2 = CustomUser.objects.create_user(
            email="student2@example.com", password="pass123", is_staff=False
        )
        self.tutor.students.add(self.student1, self.student2)
        self.client.force_authenticate(user=self.tutor)

    def test_list_tutor_students(self):
        response = self.client.get(f"/api/tutors/{self.tutor.id}/students/")
        assert response.status_code == 200
        assert response.data["student_count"] == 2
        assert len(response.data["students"]) == 2

    def test_unauthorized_access(self):
        other_tutor = CustomUser.objects.create_user(
            email="other@example.com", password="pass123", is_staff=True
        )
        self.client.force_authenticate(user=other_tutor)
        response = self.client.get(f"/api/tutors/{self.tutor.id}/students/")
        assert response.status_code == 403
