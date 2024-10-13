import pytest

from courses.models import Curriculum
from courses.serializers import (
    AssignmentSerializer,
    CourseDetailSerializer,
    CourseSummarySerializer,
    CurriculumCreateAndUpdateSerializer,
    CurriculumReadSerializer,
    CurriculumSummarySerializer,
    LectureSerializer,
    MultipleChoiceQuestionChoiceSerializer,
    MultipleChoiceQuestionSerializer,
    TopicSerializer,
)
from courses.test import conftest


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
        assert data["id"] == self.course.id
        assert data["title"] == conftest.COURSE_TITLE
        assert data["short_description"] == conftest.COURSE_SHORT_DESCRIPTION
        assert data["category"] == conftest.COURSE_CATEGORY
        assert data["skill_level"] == conftest.COURSE_SKILL_LEVEL
        assert data["price"] == conftest.COURSE_PRICE
        assert len(data["lectures"]) == 2
        assert data["lectures"][0]["title"] == conftest.LECTURE1_TITLE
        assert data["lectures"][0]["order"] == conftest.LECTURE1_ORDER
        assert data["lectures"][1]["title"] == conftest.LECTURE2_TITLE
        assert data["lectures"][1]["order"] == conftest.LECTURE2_ORDER
        assert len(data["lectures"][0]["topics"]) == 1
        assert data["lectures"][0]["topics"][0]["title"] == conftest.TOPIC1_TITLE
        assert data["lectures"][0]["topics"][0]["type"] == conftest.TOPIC1_TYPE
        assert data["lectures"][0]["topics"][0]["order"] == conftest.TOPIC1_ORDER
        assert data["lectures"][0]["topics"][0]["is_premium"] is True
        assert (
            data["lectures"][0]["topics"][0]["assignment"]["question"]
            == conftest.ASSIGNMENT_QUESTION
        )
        assert data["lectures"][1]["topics"][0]["title"] == conftest.TOPIC2_TITLE
        assert data["lectures"][1]["topics"][0]["type"] == conftest.TOPIC2_TYPE
        assert data["lectures"][1]["topics"][0]["order"] == conftest.TOPIC2_ORDER
        assert data["lectures"][1]["topics"][0]["is_premium"] is True
        assert (
            data["lectures"][1]["topics"][0]["multiple_choice_question"]["question"]
            == conftest.MCQ_QUESTION
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
            == conftest.MCQ_CHOICE1
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
            == conftest.MCQ_CHOICE2
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
            == conftest.MCQ_CHOICE3
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
            == conftest.MCQ_CHOICE4
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
            "skill_level": "beginner",
            "price": 10000,
            "thumbnail_id": 1,
            "video_id": 3,
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
                            "video_id": 1,
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
                            "video_id": 2,
                        }
                    ],
                },
            ],
        }

        # When
        serializer = CourseDetailSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Then
        assert serializer.validated_data["title"] == "Test Course"
        assert serializer.validated_data["short_description"] == "Test Course"
        assert serializer.validated_data["category"] == "JavaScript"
        assert serializer.validated_data["skill_level"] == "beginner"
        assert serializer.validated_data["price"] == 10000
        assert serializer.validated_data["lectures"][0]["title"] == "Test Lecture"
        assert serializer.validated_data["lectures"][0]["order"] == 1
        assert (
            serializer.validated_data["lectures"][0]["topics"][0]["title"]
            == "Test Topic"
        )


@pytest.mark.django_db
class TestCourseSummarySerializer:
    def test_course_summary_직렬화(self, setup_course_data):
        # Given
        course = setup_course_data["course"]

        # When
        serializer = CourseSummarySerializer(course)
        data = serializer.data

        # Then
        assert data["id"] == course.id
        assert data["title"] == conftest.COURSE_TITLE
        assert data["short_description"] == conftest.COURSE_SHORT_DESCRIPTION
        assert data["category"] == conftest.COURSE_CATEGORY
        assert data["skill_level"] == conftest.COURSE_SKILL_LEVEL
        assert data["lectures_count"] == 2

    def test_course_summary_역직렬화(self):
        # Given
        data = {
            "title": "Test Course",
            "short_description": "Test Course",
            "category": "JavaScript",
            "skill_level": "beginner",
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
        assert data["id"] == self.lecture.id
        assert data["title"] == conftest.LECTURE2_TITLE
        assert data["order"] == 2
        assert len(data["topics"]) == 1
        assert data["topics"][0]["title"] == conftest.TOPIC2_TITLE
        assert data["topics"][0]["type"] == conftest.TOPIC2_TYPE
        assert data["topics"][0]["order"] == conftest.TOPIC2_ORDER
        assert data["topics"][0]["is_premium"] is True
        assert (
            data["topics"][0]["multiple_choice_question"]["question"]
            == conftest.MCQ_QUESTION
        )
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
            == conftest.MCQ_CHOICE1
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
            == conftest.MCQ_CHOICE2
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
            == conftest.MCQ_CHOICE3
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
            == conftest.MCQ_CHOICE4
        )
        assert (
            data["topics"][0]["multiple_choice_question"][
                "multiple_choice_question_choices"
            ][3]["is_correct"]
            is False
        )


@pytest.mark.django_db
class TestTopicSerializer:

    def test_topic_직렬화(self, setup_course_data):
        # Given
        self.topic = setup_course_data["topic2"]

        # When
        serializer = TopicSerializer(self.topic)
        data = serializer.data

        # Then
        assert data["id"] == self.topic.id
        assert data["title"] == conftest.TOPIC2_TITLE
        assert data["type"] == conftest.TOPIC2_TYPE
        assert data["order"] == conftest.TOPIC2_ORDER
        assert data["is_premium"] is True
        assert data["multiple_choice_question"]["question"] == conftest.MCQ_QUESTION
        assert (
            len(data["multiple_choice_question"]["multiple_choice_question_choices"])
            == 4
        )
        assert (
            data["multiple_choice_question"]["multiple_choice_question_choices"][0][
                "choice"
            ]
            == conftest.MCQ_CHOICE1
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
            == conftest.MCQ_CHOICE2
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
            == conftest.MCQ_CHOICE3
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
            == conftest.MCQ_CHOICE4
        )
        assert (
            data["multiple_choice_question"]["multiple_choice_question_choices"][3][
                "is_correct"
            ]
            is False
        )


@pytest.mark.django_db
class TestAssignmentSerializer:
    def test_assignment_직렬화(self, setup_course_data):
        # Given
        assignment = setup_course_data["assignment"]

        # When
        serializer = AssignmentSerializer(assignment)
        data = serializer.data

        # Then
        assert data["id"] == assignment.id
        assert data["question"] == conftest.ASSIGNMENT_QUESTION

    def test_assignment_역직렬화(self):
        # Given
        data = {"question": "Test Assignment"}

        # When
        serializer = AssignmentSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Then
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
        assert data["id"] == mcq_choice.id
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
        assert data["id"] == self.mcq.id
        assert data["question"] == conftest.MCQ_QUESTION
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


@pytest.mark.django_db
class TestCurriculumCreateAndUpdateSerializer:

    def test_curriculum_create_and_update_역직렬화(self):
        # Given
        data = {
            "name": "Test Curriculum",
            "description": "Test Description",
            "price": 1000,
            "courses_ids": [1, 2, 3],
        }

        # When
        serializer = CurriculumCreateAndUpdateSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Then
        assert serializer.validated_data == data
        assert serializer.validated_data["name"] == "Test Curriculum"
        assert serializer.validated_data["description"] == "Test Description"
        assert serializer.validated_data["price"] == 1000
        assert serializer.validated_data["courses_ids"] == [1, 2, 3]


@pytest.mark.django_db
class TestCurriculumReadSerializer:

    def test_curriculum_직렬화(self, setup_course_data, create_staff_user):
        # Given
        curriculum = Curriculum.objects.create(
            name="Test Curriculum",
            description="Test Description",
            price=1000,
            author=create_staff_user,
        )
        course = setup_course_data["course"]
        curriculum.courses.add(course)

        # When
        serializer = CurriculumReadSerializer(curriculum)

        # Then
        assert serializer.data["id"] == curriculum.id
        assert serializer.data["name"] == "Test Curriculum"
        assert serializer.data["description"] == "Test Description"
        assert serializer.data["price"] == 1000
        assert serializer.data["courses"] is not None


@pytest.mark.django_db
class TestCurriculumSummarySerializer:

    def test_curriculum_summary_직렬화(self, create_staff_user):
        # Given
        curriculum = Curriculum.objects.create(
            name="Test Curriculum",
            description="Test Description",
            price=1000,
            author=create_staff_user,
        )

        # When
        serializer = CurriculumSummarySerializer(curriculum)

        # Then
        assert serializer.data["id"] == curriculum.id
        assert serializer.data["name"] == "Test Curriculum"
        assert serializer.data["price"] == 1000
        assert serializer.data["created_at"] is not None
        assert serializer.data["updated_at"] is not None
