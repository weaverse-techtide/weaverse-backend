import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from courses.models import Course

User = get_user_model()
TEST_USER_EMAIL = "testuser@example.com"
TEST_USER_PASSWORD = "testpass"
TEST_STAFF_USER_EMAIL = "staffuser@example.com"
TEST_STAFF_USER_PASSWORD = "staffpass"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user():
    return User.objects.create_user(email=TEST_USER_EMAIL, password=TEST_USER_PASSWORD)


@pytest.fixture
def create_staff_user():
    return User.objects.create_user(
        email=TEST_STAFF_USER_EMAIL, password=TEST_STAFF_USER_PASSWORD, is_staff=True
    )


def get_course_data():
    return {
        "title": "Test Course",
        "short_description": "Test Course",
        "description": {},
        "category": "JavaScript",
        "course_level": "beginner",
        "lectures": [
            {
                "title": "Test Lecture",
                "order": 1,
                "topics": [
                    {
                        "title": "Test Topic",
                        "type": "assignment",
                        "description": "Test Description",
                        "order": 1,
                        "is_premium": True,
                        "assignment": {"question": "Test Assignment"},
                    }
                ],
            },
            {
                "title": "Test Lecture 2",
                "order": 2,
                "topics": [
                    {
                        "title": "Test Topic 2",
                        "type": "quiz",
                        "description": "Test Description",
                        "order": 1,
                        "is_premium": True,
                        "multiple_choice_question": {
                            "question": "Test Multiple Choice Question",
                            "multiple_choice_question_choices": [
                                {"choice": "Choice 1", "is_correct": True},
                                {"choice": "Choice 2", "is_correct": False},
                                {"choice": "Choice 3", "is_correct": False},
                                {"choice": "Choice 4", "is_correct": False},
                            ],
                        },
                    }
                ],
            },
        ],
    }


@pytest.mark.django_db
class TestCourseList:

    def test_course_생성_요청(self, api_client, create_staff_user):
        # Given
        url = reverse("courses:course-list")
        api_client.login(
            username=TEST_STAFF_USER_EMAIL, password=TEST_STAFF_USER_PASSWORD
        )
        data = get_course_data()

        # When
        response = api_client.post(url, data, format="json")

        # Then
        assert response.status_code == status.HTTP_201_CREATED

    def test_course_생성_요청_실패_일반유저인_경우(self, api_client, create_user):
        # Given
        url = reverse("courses:course-list")
        api_client.login(username=TEST_USER_EMAIL, password=TEST_USER_PASSWORD)
        data = get_course_data()

        # When
        response = api_client.post(url, data, format="json")

        # Then
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data == {
            "detail": "이 작업을 수행할 권한(permission)이 없습니다."
        }

    def test_course_생성_요청_실패_로그인하지않은경우(self, api_client):
        # Given
        url = reverse("courses:course-list")
        data = get_course_data()

        # When
        response = api_client.post(url, data, format="json")

        # Then
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data == {
            "detail": "자격 인증데이터(authentication credentials)가 제공되지 않았습니다."
        }

    def test_course_목록_조회(self, api_client, create_user):
        # Given
        for i in range(5):
            Course.objects.create(
                title=f"Test Course {i}",
                short_description="Test Course",
                description={},
                category="JavaScript",
                course_level="beginner",
            )
        url = reverse("courses:course-list")
        api_client.login(username=TEST_USER_EMAIL, password=TEST_USER_PASSWORD)

        # When
        response = api_client.get(url)

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5
        for i in range(5):
            assert response.data[i]["title"] == f"Test Course {i}"
            assert response.data[i]["short_description"] == "Test Course"
            assert response.data[i]["category"] == "JavaScript"
            assert response.data[i]["course_level"] == "beginner"
            assert response.data[i]["created_at"] is not None
            assert response.data[i]["updated_at"] is not None
