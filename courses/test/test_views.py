import pytest
from django.urls import reverse
from rest_framework import status

from courses.models import Course, Curriculum
from courses.test import conftest


@pytest.mark.django_db
class TestCourseDetail:

    def test_course_조회(self, api_client, setup_course_data):
        # Given
        course = setup_course_data["course"]
        url = reverse("courses:course-detail", args=[course.id])
        # When
        response = api_client.get(url)

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == conftest.COURSE_TITLE
        assert response.data["short_description"] == conftest.COURSE_SHORT_DESCRIPTION
        assert response.data["category"] == conftest.COURSE_CATEGORY
        assert response.data["course_level"] == conftest.COURSE_COURSE_LEVEL
        assert response.data["created_at"] is not None
        assert response.data["updated_at"] is not None
        assert len(response.data["lectures"]) == 2
        assert len(response.data["lectures"][0]["topics"]) == 1
        assert len(response.data["lectures"][1]["topics"]) == 1
        assert (
            response.data["lectures"][0]["topics"][0]["assignment"]["question"]
            is not None
        )
        assert (
            response.data["lectures"][1]["topics"][0]["multiple_choice_question"][
                "question"
            ]
            is not None
        )
        assert (
            response.data["lectures"][1]["topics"][0]["multiple_choice_question"][
                "multiple_choice_question_choices"
            ][0]["choice"]
            is not None
        )

    def test_course_수정(self, api_client, setup_course_data):
        # Given
        course = setup_course_data["course"]
        url = reverse("courses:course-detail", args=[course.id])
        api_client.login(
            username=conftest.TEST_STAFF_USER_EMAIL,
            password=conftest.TEST_STAFF_USER_PASSWORD,
        )
        data = {
            "title": "Updated Test Course",
            "short_description": "Updated Test Course",
            "description": {},
            "category": "Python",
            "course_level": "intermediate",
            "price": 20000,
            "lectures": [
                {
                    "title": "Updated Test Lecture",
                    "order": 1,
                    "topics": [
                        {
                            "title": "Updated Test Topic",
                            "type": "assignment",
                            "description": "Updated Test Description",
                            "order": 1,
                            "is_premium": True,
                            "assignment": {"question": "Updated Test Assignment"},
                        }
                    ],
                },
                {
                    "title": "Updated Test Lecture 2",
                    "order": 2,
                    "topics": [
                        {
                            "title": "Updated Test Topic 2",
                            "type": "quiz",
                            "description": "Updated Test Description",
                            "order": 1,
                            "is_premium": True,
                            "multiple_choice_question": {
                                "question": "Updated Test Multiple Choice Question",
                                "multiple_choice_question_choices": [
                                    {"choice": "Updated Choice 1", "is_correct": True},
                                    {"choice": "Updated Choice 2", "is_correct": False},
                                    {"choice": "Updated Choice 3", "is_correct": False},
                                    {"choice": "Updated Choice 4", "is_correct": False},
                                ],
                            },
                        }
                    ],
                },
            ],
        }

        # When
        response = api_client.put(url, data, format="json")

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Updated Test Course"
        assert response.data["short_description"] == "Updated Test Course"
        assert response.data["category"] == "Python"
        assert response.data["course_level"] == "intermediate"
        assert response.data["created_at"] is not None
        assert response.data["updated_at"] is not None
        assert len(response.data["lectures"]) == 2
        assert response.data["lectures"][0]["title"] == "Updated Test Lecture"
        assert response.data["lectures"][1]["title"] == "Updated Test Lecture 2"
        assert len(response.data["lectures"][0]["topics"]) == 1
        assert len(response.data["lectures"][1]["topics"]) == 1
        assert (
            response.data["lectures"][0]["topics"][0]["assignment"]["question"]
            == "Updated Test Assignment"
        )
        assert (
            response.data["lectures"][1]["topics"][0]["multiple_choice_question"][
                "question"
            ]
            == "Updated Test Multiple Choice Question"
        )
        assert (
            response.data["lectures"][1]["topics"][0]["multiple_choice_question"][
                "multiple_choice_question_choices"
            ][0]["choice"]
            == "Updated Choice 1"
        )

    def test_course_수정_실패_로그인하지않은경우(self, api_client):
        # Given
        course = Course.objects.create(
            title="Test Course",
            short_description="Test Course",
            description={},
            category="JavaScript",
            course_level="beginner",
            price=10000,
        )
        url = reverse("courses:course-detail", args=[course.id])
        data = {
            "title": "Updated Test Course",
            "short_description": "Updated Test Course",
            "description": {},
            "category": "Python",
            "course_level": "intermediate",
            "price": 20000,
        }

        # When
        response = api_client.put(url, data, format="json")

        # Then
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data == {
            "detail": "자격 인증데이터(authentication credentials)가 제공되지 않았습니다."
        }

    def test_course_수정_실패_일반유저인_경우(self, api_client):
        # Given
        course = Course.objects.create(
            title="Test Course",
            short_description="Test Course",
            description={},
            category="JavaScript",
            course_level="beginner",
            price=10000,
        )
        url = reverse("courses:course-detail", args=[course.id])
        api_client.login(
            username=conftest.TEST_USER_EMAIL, password=conftest.TEST_USER_PASSWORD
        )
        data = {
            "title": "Updated Test Course",
            "short_description": "Updated Test Course",
            "description": {},
            "category": "Python",
            "course_level": "intermediate",
            "price": 20000,
        }

        # When
        response = api_client.put(url, data, format="json")

        # Then
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data == {
            "detail": "이 작업을 수행할 권한(permission)이 없습니다."
        }

    def test_course_삭제(self, api_client):
        # Given
        course = Course.objects.create(
            title="Test Course",
            short_description="Test Course",
            description={},
            category="JavaScript",
            course_level="beginner",
            price=10000,
        )
        url = reverse("courses:course-detail", args=[course.id])
        api_client.login(
            username=conftest.TEST_STAFF_USER_EMAIL,
            password=conftest.TEST_STAFF_USER_PASSWORD,
        )

        # When
        response = api_client.delete(url)

        # Then
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Course.objects.count() == 0

    def test_course_삭제_실패_로그인하지않은경우(self, api_client):
        # Given
        course = Course.objects.create(
            title="Test Course",
            short_description="Test Course",
            description={},
            category="JavaScript",
            course_level="beginner",
            price=10000,
        )
        url = reverse("courses:course-detail", args=[course.id])

        # When
        response = api_client.delete(url)

        # Then
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data == {
            "detail": "자격 인증데이터(authentication credentials)가 제공되지 않았습니다."
        }

    def test_course_삭제_실패_일반유저인_경우(self, api_client, create_user):
        # Given
        course = Course.objects.create(
            title="Test Course",
            short_description="Test Course",
            description={},
            category="JavaScript",
            course_level="beginner",
            price=10000,
        )
        url = reverse("courses:course-detail", args=[course.id])
        api_client.login(
            username=conftest.TEST_USER_EMAIL, password=conftest.TEST_USER_PASSWORD
        )

        # When
        response = api_client.delete(url)

        # Then
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data == {
            "detail": "이 작업을 수행할 권한(permission)이 없습니다."
        }


def get_course_data():
    return {
        "title": "Test Course",
        "short_description": "Test Course",
        "description": {},
        "category": "JavaScript",
        "course_level": "beginner",
        "price": 10000,
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
            username=conftest.TEST_STAFF_USER_EMAIL,
            password=conftest.TEST_STAFF_USER_PASSWORD,
        )
        data = get_course_data()

        # When
        response = api_client.post(url, data, format="json")

        # Then
        assert response.status_code == status.HTTP_201_CREATED

    def test_course_생성_요청_실패_일반유저인_경우(self, api_client, create_user):
        # Given
        url = reverse("courses:course-list")
        api_client.login(
            username=conftest.TEST_USER_EMAIL, password=conftest.TEST_USER_PASSWORD
        )
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
                price=10000,
            )
        url = reverse("courses:course-list")
        api_client.login(
            username=conftest.TEST_USER_EMAIL, password=conftest.TEST_USER_PASSWORD
        )

        # When
        response = api_client.get(url)

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 5


@pytest.mark.django_db
class TestCurriculumList:

    def test_curriculum_생성_요청(self, api_client, setup_course_data):
        # Given
        url = reverse("courses:curriculum-list")
        api_client.login(
            username=conftest.TEST_STAFF_USER_EMAIL,
            password=conftest.TEST_STAFF_USER_PASSWORD,
        )
        data = {
            "name": "Test Curriculum",
            "description": "Test Description",
            "price": 1000,
            "courses_ids": [setup_course_data["course"].id],
        }

        # When
        response = api_client.post(url, data, format="json")

        # Then
        assert response.status_code == status.HTTP_201_CREATED

    def test_curriculum_생성_요청_실패_일반유저인_경우(
        self, api_client, setup_course_data
    ):
        # Given
        url = reverse("courses:curriculum-list")
        api_client.login(
            username=conftest.TEST_USER_EMAIL, password=conftest.TEST_USER_PASSWORD
        )
        data = {
            "name": "Test Curriculum",
            "description": "Test Description",
            "price": 1000,
            "courses_ids": [setup_course_data["course"].id],
        }

        # When
        response = api_client.post(url, data, format="json")

        # Then
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data == {
            "detail": "이 작업을 수행할 권한(permission)이 없습니다."
        }

    def test_curriculum_생성_요청_실패_로그인하지않은경우(
        self, api_client, setup_course_data
    ):
        # Given
        url = reverse("courses:curriculum-list")
        data = {
            "name": "Test Curriculum",
            "description": "Test Description",
            "price": 1000,
            "courses_ids": [setup_course_data["course"].id],
        }

        # When
        response = api_client.post(url, data, format="json")

        # Then
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data == {
            "detail": "자격 인증데이터(authentication credentials)가 제공되지 않았습니다."
        }

    def test_curriculum_목록_조회(self, api_client, setup_course_data):
        # Given
        for i in range(5):
            Curriculum.objects.create(
                name=f"Test Curriculum {i}",
                description="Test Description",
                price=1000,
            )
        url = reverse("courses:curriculum-list")
        api_client.login(
            username=conftest.TEST_USER_EMAIL, password=conftest.TEST_USER_PASSWORD
        )

        # When
        response = api_client.get(url)

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 5


@pytest.mark.django_db
class TestCurriculumDetail:

    def test_curriculum_조회(self, api_client, setup_course_data):
        # Given
        curriculum = Curriculum.objects.create(
            name="Test Curriculum",
            description="Test Description",
            price=1000,
        )
        url = reverse("courses:curriculum-detail", args=[curriculum.id])
        course = setup_course_data["course"]
        course.curriculum = curriculum
        course.save()
        api_client.login(
            username=conftest.TEST_USER_EMAIL, password=conftest.TEST_USER_PASSWORD
        )

        # When
        response = api_client.get(url)

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Test Curriculum"
        assert response.data["description"] == "Test Description"
        assert response.data["price"] == 1000
        assert response.data["created_at"] is not None
        assert response.data["updated_at"] is not None
        assert len(response.data["courses"]) == 1

    def test_curriculum_수정(self, api_client, setup_course_data):
        # Given
        curriculum = Curriculum.objects.create(
            name="Test Curriculum",
            description="Test Description",
            price=1000,
        )
        url = reverse("courses:curriculum-detail", args=[curriculum.id])
        api_client.login(
            username=conftest.TEST_STAFF_USER_EMAIL,
            password=conftest.TEST_STAFF_USER_PASSWORD,
        )
        data = {
            "name": "Updated Test Curriculum",
            "description": "Updated Test Description",
            "price": 2000,
            "courses_ids": [setup_course_data["course"].id],
        }

        # When
        response = api_client.put(url, data, format="json")

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated Test Curriculum"
        assert response.data["description"] == "Updated Test Description"
        assert response.data["price"] == 2000

    def test_curriculum_수정_실패_일반유저인_경우(self, api_client, setup_course_data):
        # Given
        curriculum = Curriculum.objects.create(
            name="Test Curriculum",
            description="Test Description",
            price=1000,
        )
        url = reverse("courses:curriculum-detail", args=[curriculum.id])
        api_client.login(
            username=conftest.TEST_USER_EMAIL, password=conftest.TEST_USER_PASSWORD
        )
        data = {
            "name": "Updated Test Curriculum",
            "description": "Updated Test Description",
            "price": 2000,
            "courses_ids": [setup_course_data["course"].id],
        }

        # When
        response = api_client.put(url, data, format="json")

        # Then
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data == {
            "detail": "이 작업을 수행할 권한(permission)이 없습니다."
        }

    def test_curriculum_수정_실패_로그인하지않은경우(
        self, api_client, setup_course_data
    ):
        # Given
        curriculum = Curriculum.objects.create(
            name="Test Curriculum",
            description="Test Description",
            price=1000,
        )
        url = reverse("courses:curriculum-detail", args=[curriculum.id])
        data = {
            "name": "Updated Test Curriculum",
            "description": "Updated Test Description",
            "price": 2000,
            "courses_ids": [setup_course_data["course"].id],
        }

        # When
        response = api_client.put(url, data, format="json")

        # Then
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data == {
            "detail": "자격 인증데이터(authentication credentials)가 제공되지 않았습니다."
        }

    def test_curriculum_삭제(self, api_client):
        # Given
        curriculum = Curriculum.objects.create(
            name="Test Curriculum",
            description="Test Description",
            price=1000,
        )
        url = reverse("courses:curriculum-detail", args=[curriculum.id])
        api_client.login(
            username=conftest.TEST_STAFF_USER_EMAIL,
            password=conftest.TEST_STAFF_USER_PASSWORD,
        )

        # When
        response = api_client.delete(url)

        # Then
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Curriculum.objects.count() == 0

    def test_curriculum_삭제_실패_일반유저인_경우(self, api_client):
        # Given
        curriculum = Curriculum.objects.create(
            name="Test Curriculum",
            description="Test Description",
            price=1000,
        )
        url = reverse("courses:curriculum-detail", args=[curriculum.id])
        api_client.login(
            username=conftest.TEST_USER_EMAIL, password=conftest.TEST_USER_PASSWORD
        )

        # When
        response = api_client.delete(url)

        # Then
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data == {
            "detail": "이 작업을 수행할 권한(permission)이 없습니다."
        }

    def test_curriculum_삭제_실패_로그인하지않은경우(self, api_client):
        # Given
        curriculum = Curriculum.objects.create(
            name="Test Curriculum",
            description="Test Description",
            price=1000,
        )
        url = reverse("courses:curriculum-detail", args=[curriculum.id])

        # When
        response = api_client.delete(url)

        # Then
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data == {
            "detail": "자격 인증데이터(authentication credentials)가 제공되지 않았습니다."
        }

    def test_curriculum_수정_실패_존재하지않는_curriculum인_경우(self, api_client):
        # Given
        url = reverse("courses:curriculum-detail", args=[1])
        api_client.login(
            username=conftest.TEST_STAFF_USER_EMAIL,
            password=conftest.TEST_STAFF_USER_PASSWORD,
        )
        data = {
            "name": "Updated Test Curriculum",
            "description": "Updated Test Description",
            "price": 2000,
            "courses_ids": [],
        }

        # When
        response = api_client.put(url, data, format="json")

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data is not None
