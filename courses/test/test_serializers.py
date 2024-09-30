import pytest

from courses.models import (
    Assignment,
    Course,
    Lecture,
    MultipleChoiceQuestion,
    MultipleChoiceQuestionChoice,
    Topic,
)
from courses.serializers import (
    AssignmentSerializer,
    CourseDetailSerializer,
    CourseSummarySerializer,
    LectureSerializer,
    MultipleChoiceQuestionChoiceSerializer,
    MultipleChoiceQuestionSerializer,
    TopicSerializer,
)

# 테스트에서 사용할 상수를 정의합니다.
COURSE_TITLE = "Test Course"
COURSE_SHORT_DESCRIPTION = "Test Course"
COURSE_DESCRIPTION = {}
COURSE_CATEGORY = "JavaScript"
COURSE_COURSE_LEVEL = "beginner"
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


@pytest.fixture(autouse=True)
def setup_course_data():
    """
    테스트에서 사용할 Course, Lecture, Topic, Assignment, MultipleChoiceQuestion, MultipleChoiceQuestionChoice 인스턴스를 생성합니다.
    """

    course = Course.objects.create(
        title=COURSE_TITLE,
        short_description=COURSE_SHORT_DESCRIPTION,
        description=COURSE_DESCRIPTION,
        category=COURSE_CATEGORY,
        course_level=COURSE_COURSE_LEVEL,
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
        description=TOPIC1_DESCRIPTION,
        order=1,
        is_premium=True,
    )
    topic2 = Topic.objects.create(
        title=TOPIC2_TITLE,
        lecture=lecture2,
        type=TOPIC2_TYPE,
        description=TOPIC2_DESCRIPTION,
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


@pytest.mark.django_db
class TestCourseDetailSerializer:
    """
    CourseSerializer 테스트
    """

    def test_course_직렬화(self, setup_course_data):
        # Given
        self.course = setup_course_data["course"]

        # When
        serializer = CourseDetailSerializer(self.course)
        data = serializer.data

        # Then
        assert data["title"] == COURSE_TITLE
        assert data["short_description"] == COURSE_SHORT_DESCRIPTION
        assert data["description"] == COURSE_DESCRIPTION
        assert data["category"] == COURSE_CATEGORY
        assert data["course_level"] == COURSE_COURSE_LEVEL
        assert len(data["lectures"]) == 2
        assert data["lectures"][0]["title"] == LECTURE1_TITLE
        assert data["lectures"][0]["order"] == LECTURE1_ORDER
        assert data["lectures"][1]["title"] == LECTURE2_TITLE
        assert data["lectures"][1]["order"] == LECTURE2_ORDER
        assert len(data["lectures"][0]["topics"]) == 1
        assert data["lectures"][0]["topics"][0]["title"] == TOPIC1_TITLE
        assert data["lectures"][0]["topics"][0]["type"] == TOPIC1_TYPE
        assert data["lectures"][0]["topics"][0]["description"] == TOPIC1_DESCRIPTION
        assert data["lectures"][0]["topics"][0]["order"] == TOPIC1_ORDER
        assert data["lectures"][0]["topics"][0]["is_premium"] is True
        assert (
            data["lectures"][0]["topics"][0]["assignment"]["question"]
            == ASSIGNMENT_QUESTION
        )
        assert data["lectures"][1]["topics"][0]["title"] == TOPIC2_TITLE
        assert data["lectures"][1]["topics"][0]["type"] == TOPIC2_TYPE
        assert data["lectures"][1]["topics"][0]["description"] == TOPIC2_DESCRIPTION
        assert data["lectures"][1]["topics"][0]["order"] == TOPIC2_ORDER
        assert data["lectures"][1]["topics"][0]["is_premium"] is True
        assert (
            data["lectures"][1]["topics"][0]["multiple_choice_question"]["question"]
            == MCQ_QUESTION
        )
        assert (
            len(
                data["lectures"][1]["topics"][0]["multiple_choice_question"][
                    "multiple_choice_question_choices"
                ]
            )
            == 4
        )
        assert (
            data["lectures"][1]["topics"][0]["multiple_choice_question"][
                "multiple_choice_question_choices"
            ][0]["choice"]
            == MCQ_CHOICE1
        )
        assert (
            data["lectures"][1]["topics"][0]["multiple_choice_question"][
                "multiple_choice_question_choices"
            ][0]["is_correct"]
            is True
        )
        assert (
            data["lectures"][1]["topics"][0]["multiple_choice_question"][
                "multiple_choice_question_choices"
            ][1]["choice"]
            == MCQ_CHOICE2
        )
        assert (
            data["lectures"][1]["topics"][0]["multiple_choice_question"][
                "multiple_choice_question_choices"
            ][1]["is_correct"]
            is False
        )
        assert (
            data["lectures"][1]["topics"][0]["multiple_choice_question"][
                "multiple_choice_question_choices"
            ][2]["choice"]
            == MCQ_CHOICE3
        )
        assert (
            data["lectures"][1]["topics"][0]["multiple_choice_question"][
                "multiple_choice_question_choices"
            ][2]["is_correct"]
            is False
        )
        assert (
            data["lectures"][1]["topics"][0]["multiple_choice_question"][
                "multiple_choice_question_choices"
            ][3]["choice"]
            == MCQ_CHOICE4
        )
        assert (
            data["lectures"][1]["topics"][0]["multiple_choice_question"][
                "multiple_choice_question_choices"
            ][3]["is_correct"]
            is False
        )

    def test_course_역직렬화(self):
        # Given
        data = {
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
                            "type": "quiz",
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
                            "type": "assignment",
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

        # When
        serializer = CourseDetailSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Then
        assert serializer.validated_data == data


@pytest.mark.django_db
class TestCourseSummarySerializer:
    def test_course_직렬화(self, setup_course_data):
        # Given
        course = setup_course_data["course"]

        # When
        serializer = CourseSummarySerializer(course)
        data = serializer.data

        # Then
        assert data["title"] == COURSE_TITLE
        assert data["short_description"] == COURSE_SHORT_DESCRIPTION
        assert data["category"] == COURSE_CATEGORY
        assert data["course_level"] == COURSE_COURSE_LEVEL

    def test_course_역직렬화(self):
        # Given
        data = {
            "title": "Test Course",
            "short_description": "Test Course",
            "category": "JavaScript",
            "course_level": "beginner",
        }

        # When
        serializer = CourseSummarySerializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Then
        assert serializer.validated_data == data


@pytest.mark.django_db
class TestLectureSerializer:

    def test_lecture_직렬화(self, setup_course_data):
        # Given
        self.lecture = setup_course_data["lecture2"]

        # When
        serializer = LectureSerializer(self.lecture)
        data = serializer.data

        # Then
        assert data["title"] == LECTURE2_TITLE
        assert data["order"] == 2
        assert len(data["topics"]) == 1
        assert data["topics"][0]["title"] == TOPIC2_TITLE
        assert data["topics"][0]["type"] == TOPIC2_TYPE
        assert data["topics"][0]["description"] == TOPIC2_DESCRIPTION
        assert data["topics"][0]["order"] == TOPIC2_ORDER
        assert data["topics"][0]["is_premium"] is True
        assert data["topics"][0]["multiple_choice_question"]["question"] == MCQ_QUESTION
        assert (
            len(
                data["topics"][0]["multiple_choice_question"][
                    "multiple_choice_question_choices"
                ]
            )
            == 4
        )
        assert (
            data["topics"][0]["multiple_choice_question"][
                "multiple_choice_question_choices"
            ][0]["choice"]
            == MCQ_CHOICE1
        )
        assert (
            data["topics"][0]["multiple_choice_question"][
                "multiple_choice_question_choices"
            ][0]["is_correct"]
            is True
        )
        assert (
            data["topics"][0]["multiple_choice_question"][
                "multiple_choice_question_choices"
            ][1]["choice"]
            == MCQ_CHOICE2
        )
        assert (
            data["topics"][0]["multiple_choice_question"][
                "multiple_choice_question_choices"
            ][1]["is_correct"]
            is False
        )
        assert (
            data["topics"][0]["multiple_choice_question"][
                "multiple_choice_question_choices"
            ][2]["choice"]
            == MCQ_CHOICE3
        )
        assert (
            data["topics"][0]["multiple_choice_question"][
                "multiple_choice_question_choices"
            ][2]["is_correct"]
            is False
        )
        assert (
            data["topics"][0]["multiple_choice_question"][
                "multiple_choice_question_choices"
            ][3]["choice"]
            == MCQ_CHOICE4
        )
        assert (
            data["topics"][0]["multiple_choice_question"][
                "multiple_choice_question_choices"
            ][3]["is_correct"]
            is False
        )

    def test_lecture_역직렬화(self):
        # Given
        data = {
            "title": "Test Lecture",
            "order": 1,
            "topics": [
                {
                    "title": "Test Topic",
                    "type": "quiz",
                    "description": "Test Description",
                    "order": 1,
                    "is_premium": True,
                    "assignment": {"question": "Test Assignment"},
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
        }

        # When
        serializer = LectureSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Then
        assert serializer.validated_data == data


@pytest.mark.django_db
class TestTopicSerializer:

    def test_topic_직렬화(self, setup_course_data):
        # Given
        self.topic = setup_course_data["topic2"]

        # When
        serializer = TopicSerializer(self.topic)
        data = serializer.data

        # Then
        assert data["title"] == TOPIC2_TITLE
        assert data["type"] == TOPIC2_TYPE
        assert data["description"] == TOPIC2_DESCRIPTION
        assert data["order"] == TOPIC2_ORDER
        assert data["is_premium"] is True
        assert data["multiple_choice_question"]["question"] == MCQ_QUESTION
        assert (
            len(data["multiple_choice_question"]["multiple_choice_question_choices"])
            == 4
        )
        assert (
            data["multiple_choice_question"]["multiple_choice_question_choices"][0][
                "choice"
            ]
            == MCQ_CHOICE1
        )
        assert (
            data["multiple_choice_question"]["multiple_choice_question_choices"][0][
                "is_correct"
            ]
            is True
        )
        assert (
            data["multiple_choice_question"]["multiple_choice_question_choices"][1][
                "choice"
            ]
            == MCQ_CHOICE2
        )
        assert (
            data["multiple_choice_question"]["multiple_choice_question_choices"][1][
                "is_correct"
            ]
            is False
        )
        assert (
            data["multiple_choice_question"]["multiple_choice_question_choices"][2][
                "choice"
            ]
            == MCQ_CHOICE3
        )
        assert (
            data["multiple_choice_question"]["multiple_choice_question_choices"][2][
                "is_correct"
            ]
            is False
        )
        assert (
            data["multiple_choice_question"]["multiple_choice_question_choices"][3][
                "choice"
            ]
            == MCQ_CHOICE4
        )
        assert (
            data["multiple_choice_question"]["multiple_choice_question_choices"][3][
                "is_correct"
            ]
            is False
        )

    def test_topic_역직렬화(self):
        # Given
        data = {
            "title": "Test Topic",
            "type": "quiz",
            "description": "Test Description",
            "order": 1,
            "is_premium": True,
            "assignment": {"question": "Test Assignment"},
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

        # When
        serializer = TopicSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Then
        assert serializer.validated_data == data


@pytest.mark.django_db
class TestAssignmentSerializer:
    def test_assignment_직렬화(self, setup_course_data):
        # Given
        assignment = setup_course_data["assignment"]

        # When
        serializer = AssignmentSerializer(assignment)
        data = serializer.data

        # Then
        assert data["question"] == "Test Assignment"

    def test_assignment_역직렬화(self):
        data = {"question": "Test Assignment"}

        serializer = AssignmentSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        assert serializer.validated_data == data
        assert serializer.validated_data["question"] == "Test Assignment"


@pytest.mark.django_db
class TestMultipleChoiceQuestionChoiceSerializer:
    def test_multiple_choice_question_choice_직렬화(self, setup_course_data):
        # Given
        mcq_choice = setup_course_data["choice1"]

        # When
        serializer = MultipleChoiceQuestionChoiceSerializer(mcq_choice)
        data = serializer.data

        # Then
        assert data["choice"] == "Choice 1"
        assert data["is_correct"] is True

    def test_multiple_choice_question_choice_역직렬화(self):
        # Given
        data = {"choice": "Choice 1", "is_correct": True}

        # When
        serializer = MultipleChoiceQuestionChoiceSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Then
        assert serializer.validated_data == data
        assert serializer.validated_data["choice"] == "Choice 1"
        assert serializer.validated_data["is_correct"] is True


@pytest.mark.django_db
class TestMultipleChoiceQuestionSerializer:
    def test_multiple_choice_question_직렬화(self, setup_course_data):
        # Given
        self.mcq = setup_course_data["mcq"]

        # When
        serializer = MultipleChoiceQuestionSerializer(self.mcq)
        data = serializer.data

        # Then
        assert data["question"] == "Test Multiple Choice Question"
        assert len(data["multiple_choice_question_choices"]) == 4
        assert data["multiple_choice_question_choices"][0]["choice"] == "Choice 1"
        assert data["multiple_choice_question_choices"][0]["is_correct"] is True
        assert data["multiple_choice_question_choices"][1]["choice"] == "Choice 2"
        assert data["multiple_choice_question_choices"][1]["is_correct"] is False
        assert data["multiple_choice_question_choices"][2]["choice"] == "Choice 3"
        assert data["multiple_choice_question_choices"][2]["is_correct"] is False
        assert data["multiple_choice_question_choices"][3]["choice"] == "Choice 4"
        assert data["multiple_choice_question_choices"][3]["is_correct"] is False

    def test_multiple_choice_question_역직렬화(self):
        # Given
        data = {
            "question": "Test Multiple Choice Question",
            "multiple_choice_question_choices": [
                {"choice": "Choice 1", "is_correct": True},
                {"choice": "Choice 2", "is_correct": False},
                {"choice": "Choice 3", "is_correct": False},
                {"choice": "Choice 4", "is_correct": False},
            ],
        }

        # When
        serializer = MultipleChoiceQuestionSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Then
        assert serializer.validated_data == data
        assert serializer.validated_data["question"] == "Test Multiple Choice Question"
        assert len(serializer.validated_data["multiple_choice_question_choices"]) == 4
        assert (
            serializer.validated_data["multiple_choice_question_choices"][0]["choice"]
            == "Choice 1"
        )
        assert (
            serializer.validated_data["multiple_choice_question_choices"][0][
                "is_correct"
            ]
            is True
        )
        assert (
            serializer.validated_data["multiple_choice_question_choices"][1]["choice"]
            == "Choice 2"
        )
        assert (
            serializer.validated_data["multiple_choice_question_choices"][1][
                "is_correct"
            ]
            is False
        )
        assert (
            serializer.validated_data["multiple_choice_question_choices"][2]["choice"]
            == "Choice 3"
        )
        assert (
            serializer.validated_data["multiple_choice_question_choices"][2][
                "is_correct"
            ]
            is False
        )
        assert (
            serializer.validated_data["multiple_choice_question_choices"][3]["choice"]
            == "Choice 4"
        )
        assert (
            serializer.validated_data["multiple_choice_question_choices"][3][
                "is_correct"
            ]
            is False
        )
