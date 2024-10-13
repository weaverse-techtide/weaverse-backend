import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from courses.models import (
    Assignment,
    Course,
    Lecture,
    MultipleChoiceQuestion,
    MultipleChoiceQuestionChoice,
    Topic,
)
from jwtauth.utils.token_generator import generate_access_token
from materials.models import Image, Video

# 테스트에서 사용할 상수를 정의합니다.
COURSE_TITLE = "Test Course"
COURSE_SHORT_DESCRIPTION = "Test Course"
COURSE_DESCRIPTION = {}
COURSE_CATEGORY = "JavaScript"
COURSE_SKILL_LEVEL = "beginner"
COURSE_PRICE = 10000
LECTURE1_TITLE = "Test Lecture 1"
LECTURE1_ORDER = 1
LECTURE2_TITLE = "Test Lecture 2"
LECTURE2_ORDER = 2
TOPIC1_TITLE = "Test Topic 1"
TOPIC1_TYPE = "quiz"
TOPIC1_DESCRIPTION = "Test Description"
TOPIC1_ORDER = 1
TOPIC1_IS_PREMIUM = True
TOPIC2_TITLE = "Test Topic 2"
TOPIC2_TYPE = "assignment"
TOPIC2_DESCRIPTION = "Test Description"
TOPIC2_ORDER = 2
TOPIC2_IS_PREMIUM = True
ASSIGNMENT_QUESTION = "Test Assignment"
MCQ_QUESTION = "Test Multiple Choice Question"
MCQ_CHOICE1 = "Choice 1"
MCQ_CHOICE2 = "Choice 2"
MCQ_CHOICE3 = "Choice 3"
MCQ_CHOICE4 = "Choice 4"
TEST_USER_EMAIL = "testuser@example.com"
TEST_USER_PASSWORD = "testpass"
TEST_STAFF_USER_EMAIL = "staffuser@example.com"
TEST_STAFF_USER_PASSWORD = "staffpass"


@pytest.fixture
def setup_course_data(create_staff_user):
    """
    테스트에서 사용할 Course, Lecture, Topic, Assignment, MultipleChoiceQuestion, MultipleChoiceQuestionChoice 인스턴스를 생성합니다.
    """

    course = Course.objects.create(
        title=COURSE_TITLE,
        author=create_staff_user,
        short_description=COURSE_SHORT_DESCRIPTION,
        description=COURSE_DESCRIPTION,
        category=COURSE_CATEGORY,
        skill_level=COURSE_SKILL_LEVEL,
        price=COURSE_PRICE,
    )
    lecture1 = Lecture.objects.create(
        title=LECTURE1_TITLE,
        course=course,
        order=LECTURE1_ORDER,
    )
    lecture2 = Lecture.objects.create(
        title=LECTURE2_TITLE, course=course, order=LECTURE2_ORDER
    )
    topic1 = Topic.objects.create(
        title=TOPIC1_TITLE,
        lecture=lecture1,
        type=TOPIC1_TYPE,
        order=1,
        is_premium=True,
    )
    topic2 = Topic.objects.create(
        title=TOPIC2_TITLE,
        lecture=lecture2,
        type=TOPIC2_TYPE,
        order=TOPIC2_ORDER,
        is_premium=True,
    )
    assignment = Assignment.objects.create(question=ASSIGNMENT_QUESTION, topic=topic1)
    mcq = MultipleChoiceQuestion.objects.create(
        question=MCQ_QUESTION,
        topic=topic2,
    )
    choice1 = MultipleChoiceQuestionChoice.objects.create(
        choice=MCQ_CHOICE1,
        is_correct=True,
        question=mcq,
    )
    choice2 = MultipleChoiceQuestionChoice.objects.create(
        choice=MCQ_CHOICE2,
        is_correct=False,
        question=mcq,
    )
    choice3 = MultipleChoiceQuestionChoice.objects.create(
        choice=MCQ_CHOICE3,
        is_correct=False,
        question=mcq,
    )
    choice4 = MultipleChoiceQuestionChoice.objects.create(
        choice=MCQ_CHOICE4,
        is_correct=False,
        question=mcq,
    )
    return {
        "course": course,
        "lecture1": lecture1,
        "lecture2": lecture2,
        "topic1": topic1,
        "topic2": topic2,
        "assignment": assignment,
        "mcq": mcq,
        "choice1": choice1,
        "choice2": choice2,
        "choice3": choice3,
        "choice4": choice4,
    }


User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture(autouse=True)
def create_user():
    user = User.objects.create_user(
        email=TEST_USER_EMAIL, password=TEST_USER_PASSWORD, nickname="testuser"
    )
    Image.objects.create(user=user, image_url="test.jpg")
    return user


@pytest.fixture(autouse=True)
def create_staff_user():
    user = User.objects.create_user(
        email=TEST_STAFF_USER_EMAIL,
        password=TEST_STAFF_USER_PASSWORD,
        is_staff=True,
        nickname="staffuser",
    )
    Image.objects.create(user=user, image_url="test.jpg")
    return user


@pytest.fixture()
def user_token(create_user):
    return generate_access_token(create_user)


@pytest.fixture()
def staff_user_token(create_staff_user):
    return generate_access_token(create_staff_user)


@pytest.fixture
def create_video():
    return Video.objects.create(
        video_url="https://www.youtube.com/watch?v=123456",
    )
