import pytest

from courses.mixins import CourseMixin
from courses.models import Course, Lecture, MultipleChoiceQuestion, Topic


@pytest.mark.django_db
class TestCourseMixin:

    def test_create_course_with_lectures_and_topics(self, create_staff_user):
        # Given
        course_mixin = CourseMixin()
        course_data = {
            "title": "course_title",
            "short_description": "course_short_description",
            "description": "course_description",
            "category": "JavaScript",
            "skill_level": "beginner",
            "price": 10000,
        }
        lectures_data = [
            {
                "title": "lecture_title",
                "order": 1,
                "topics": [
                    {
                        "title": "topic_title1",
                        "type": "assignment",
                        "description": "topic_description1",
                        "order": 1,
                        "is_premium": True,
                        "assignment": {
                            "question": "question1",
                        },
                    },
                    {
                        "title": "topic_title2",
                        "type": "quiz",
                        "description": "topic_description2",
                        "order": 2,
                        "is_premium": True,
                        "multiple_choice_question": {
                            "question": "question2",
                            "multiple_choice_question_choices": [
                                {"choice": "choice1", "is_correct": False},
                                {"choice": "choice2", "is_correct": False},
                                {"choice": "choice3", "is_correct": False},
                                {"choice": "choice4", "is_correct": True},
                            ],
                        },
                    },
                ],
            },
            {
                "title": "lecture_title2",
                "order": 2,
                "topics": [
                    {
                        "title": "topic_title3",
                        "type": "assignment",
                        "description": "topic_description3",
                        "order": 1,
                        "is_premium": True,
                        "assignment": {
                            "question": "question3",
                        },
                    },
                    {
                        "title": "topic_title4",
                        "type": "quiz",
                        "description": "topic_description4",
                        "order": 2,
                        "is_premium": True,
                        "multiple_choice_question": {
                            "question": "question4",
                            "multiple_choice_question_choices": [
                                {"choice": "choice1", "is_correct": False},
                                {"choice": "choice2", "is_correct": False},
                                {"choice": "choice3", "is_correct": False},
                                {"choice": "choice4", "is_correct": True},
                            ],
                        },
                    },
                ],
            },
        ]

        # When
        course = course_mixin.create_course_with_lectures_and_topics(
            course_data, lectures_data, create_staff_user
        )

        # Then
        course = (
            Course.objects.filter(id=course.id)
            .prefetch_related(
                "lectures__topics__assignment",
                "lectures__topics__multiple_choice_question__multiple_choice_question_choices",
            )
            .first()
        )
        assert course is not None
        assert course.title == course_data["title"]
        assert course.short_description == course_data["short_description"]
        assert course.description == course_data["description"]
        assert course.category == course_data["category"]
        assert course.skill_level == course_data["skill_level"]
        assert course.price == course_data["price"]

        lectures = course.lectures.all()
        assert lectures.count() == 2

        topics1 = lectures[0].topics.all()
        assert topics1.count() == 2
        assert topics1[0].assignment is not None
        assert topics1[1].multiple_choice_question is not None
        assert (
            topics1[1].multiple_choice_question.multiple_choice_question_choices.count()
            == 4
        )

        topics2 = lectures[1].topics.all()
        assert topics2.count() == 2
        assert topics2[0].assignment is not None
        assert topics2[1].multiple_choice_question is not None
        assert (
            topics2[1].multiple_choice_question.multiple_choice_question_choices.count()
            == 4
        )

    def test_create_course(self, create_staff_user):
        # Given
        course_mixin = CourseMixin()
        course_data = {
            "title": "course_title",
            "short_description": "course_short_description",
            "description": "course_description",
            "category": "JavaScript",
            "skill_level": "beginner",
            "price": 10000,
        }

        # When
        course = course_mixin._create_course(course_data, create_staff_user)

        # Then
        assert course is not None
        assert course.title == course_data["title"]
        assert course.short_description == course_data["short_description"]
        assert course.description == course_data["description"]
        assert course.category == course_data["category"]
        assert course.skill_level == course_data["skill_level"]

    def test_create_lecture(self, create_staff_user):
        # Given
        course_mixin = CourseMixin()
        lecture_data = {
            "title": "lecture_title",
            "order": 1,
        }
        course = Course.objects.create(
            title="course_title",
            category="JavaScript",
            skill_level="beginner",
            short_description="course_short_description",
            description="course_description",
            price=10000,
            author=create_staff_user,
        )

        # When
        lecture = course_mixin._create_lecture(lecture_data, course)

        # Then
        assert lecture is not None
        assert lecture.title == lecture_data["title"]
        assert lecture.order == lecture_data["order"]
        assert lecture.course == course

    def test_create_topic(self, create_staff_user):
        # Given
        course_mixin = CourseMixin()
        topic_data = {
            "title": "topic_title",
            "type": "assignment",
            "description": "topic_description",
            "order": 1,
            "is_premium": True,
        }
        lecture = Course.objects.create(
            title="course_title",
            category="JavaScript",
            skill_level="beginner",
            short_description="course_short_description",
            description="course_description",
            price=10000,
            author=create_staff_user,
        ).lectures.create(title="lecture_title", order=1)

        # When
        topic = course_mixin._create_topic(topic_data, lecture)

        # Then
        assert topic is not None
        assert topic.title == topic_data["title"]
        assert topic.type == topic_data["type"]
        assert topic.description == topic_data["description"]
        assert topic.order == topic_data["order"]
        assert topic.is_premium == topic_data["is_premium"]
        assert topic.lecture == lecture

    def test_handle_topic_type_assignment(self, create_staff_user):
        # Given
        course_mixin = CourseMixin()
        topic_data = {
            "title": "topic_title",
            "type": "assignment",
            "description": "topic_description",
            "order": 1,
            "is_premium": True,
            "assignment": {
                "question": "question",
            },
        }
        lecture = Course.objects.create(
            title="course_title",
            category="JavaScript",
            skill_level="beginner",
            short_description="course_short_description",
            description="course_description",
            price=10000,
            author=create_staff_user,
        ).lectures.create(title="lecture_title", order=1)

        # When
        topic = course_mixin._create_topic(topic_data, lecture)
        course_mixin._handle_topic_type(topic, topic_data)

        # Then
        assert topic.assignment is not None
        assert topic.assignment.question == topic_data["assignment"]["question"]

    def test_handle_topic_type_quiz(self, create_staff_user):
        # Given
        course_mixin = CourseMixin()
        topic_data = {
            "title": "topic_title",
            "type": "quiz",
            "description": "topic_description",
            "order": 1,
            "is_premium": True,
            "multiple_choice_question": {
                "question": "question",
                "multiple_choice_question_choices": [
                    {"choice": "choice1", "is_correct": False},
                    {"choice": "choice2", "is_correct": False},
                    {"choice": "choice3", "is_correct": False},
                    {"choice": "choice4", "is_correct": True},
                ],
            },
        }
        lecture = Course.objects.create(
            title="course_title",
            category="JavaScript",
            skill_level="beginner",
            short_description="course_short_description",
            description="course_description",
            price=10000,
            author=create_staff_user,
        ).lectures.create(title="lecture_title", order=1)

        # When
        topic = course_mixin._create_topic(topic_data, lecture)
        course_mixin._handle_topic_type(topic, topic_data)

        # Then
        assert topic.multiple_choice_question is not None
        assert (
            topic.multiple_choice_question.question
            == topic_data["multiple_choice_question"]["question"]
        )
        assert (
            topic.multiple_choice_question.multiple_choice_question_choices.count() == 4
        )

    def test_create_assignment(self, create_staff_user):
        # Given
        course_mixin = CourseMixin()
        assignment_data = {
            "question": "question",
        }
        topic = (
            Course.objects.create(
                title="course_title",
                category="JavaScript",
                skill_level="beginner",
                short_description="course_short_description",
                description="course_description",
                price=10000,
                author=create_staff_user,
            )
            .lectures.create(title="lecture_title", order=1)
            .topics.create(
                title="topic_title",
                type="assignment",
                description="topic_description",
                order=1,
                is_premium=True,
            )
        )

        # When
        course_mixin._create_assignment(topic, assignment_data)

        # Then
        assert topic.assignment is not None
        assert topic.assignment.question == assignment_data["question"]

    def test_create_quiz(self, create_staff_user):
        # Given
        course_mixin = CourseMixin()
        multiple_choice_question_data = {
            "question": "question",
            "multiple_choice_question_choices": [
                {"choice": "choice1", "is_correct": False},
                {"choice": "choice2", "is_correct": False},
                {"choice": "choice3", "is_correct": False},
                {"choice": "choice4", "is_correct": True},
            ],
        }
        topic = (
            Course.objects.create(
                title="course_title",
                category="JavaScript",
                skill_level="beginner",
                short_description="course_short_description",
                description="course_description",
                price=10000,
                author=create_staff_user,
            )
            .lectures.create(title="lecture_title", order=1)
            .topics.create(
                title="topic_title",
                type="quiz",
                description="topic_description",
                order=1,
                is_premium=True,
            )
        )

        # When
        course_mixin._create_quiz(topic, multiple_choice_question_data)

        # Then
        assert topic.multiple_choice_question is not None
        assert (
            topic.multiple_choice_question.question
            == multiple_choice_question_data["question"]
        )
        assert (
            topic.multiple_choice_question.multiple_choice_question_choices.count() == 4
        )
        assert (
            topic.multiple_choice_question.multiple_choice_question_choices.filter(
                is_correct=True
            ).count()
            == 1
        )

    def test_create_multiple_choice_question_choice(self, create_staff_user):
        # Given
        course_mixin = CourseMixin()
        course = Course.objects.create(
            title="course_title",
            category="JavaScript",
            skill_level="beginner",
            short_description="course_short_description",
            description="course_description",
            price=10000,
            author=create_staff_user,
        )
        lecture = Lecture.objects.create(title="lecture_title", course=course, order=1)
        topic = Topic.objects.create(
            title="topic_title",
            lecture=lecture,
            type="quiz",
            description="topic_description",
            order=1,
            is_premium=True,
        )
        multiple_choice_question = MultipleChoiceQuestion.objects.create(
            question="question", topic=topic
        )
        multiple_choice_question_choice_data = {
            "choice": "choice",
            "is_correct": True,
        }

        # When
        course_mixin._create_multiple_choice_question_choice(
            multiple_choice_question, multiple_choice_question_choice_data
        )

        # Then
        assert (
            multiple_choice_question.multiple_choice_question_choices.filter(
                choice=multiple_choice_question_choice_data["choice"],
                is_correct=multiple_choice_question_choice_data["is_correct"],
            ).count()
            == 1
        )

    def test_create_multiple_choice_question(self, create_staff_user):
        # Given
        course_mixin = CourseMixin()
        course = Course.objects.create(
            title="course_title",
            category="JavaScript",
            skill_level="beginner",
            short_description="course_short_description",
            description="course_description",
            price=10000,
            author=create_staff_user,
        )
        lecture = Lecture.objects.create(title="lecture_title", course=course, order=1)
        topic = Topic.objects.create(
            title="topic_title",
            lecture=lecture,
            type="quiz",
            description="topic_description",
            order=1,
            is_premium=True,
        )
        multiple_choice_question_data = {
            "question": "question",
            "multiple_choice_question_choices": [
                {"choice": "choice1", "is_correct": False},
                {"choice": "choice2", "is_correct": False},
                {"choice": "choice3", "is_correct": False},
                {"choice": "choice4", "is_correct": True},
            ],
        }

        # When
        multiple_choice_question = course_mixin._create_quiz(
            topic, multiple_choice_question_data
        )

        # Then
        assert multiple_choice_question is not None
        assert (
            multiple_choice_question.question
            == multiple_choice_question_data["question"]
        )
        assert multiple_choice_question.multiple_choice_question_choices.count() == 4
        assert (
            multiple_choice_question.multiple_choice_question_choices.filter(
                is_correct=True
            ).count()
            == 1
        )

    def test_update_course(self, create_staff_user):
        # Given
        course_mixin = CourseMixin()
        course = Course.objects.create(
            title="course_title",
            category="JavaScript",
            skill_level="beginner",
            short_description="course_short_description",
            description="course_description",
            price=10000,
            author=create_staff_user,
        )
        course_data = {
            "title": "updated_course_title",
            "short_description": "updated_course_short_description",
            "description": "updated_course_description",
            "category": "Python",
            "skill_level": "intermediate",
            "price": 20000,
        }
        lectures_data = [
            {
                "title": "updated_lecture_title",
                "order": 1,
                "topics": [
                    {
                        "title": "updated_topic_title1",
                        "type": "assignment",
                        "description": "updated_topic_description1",
                        "order": 1,
                        "is_premium": True,
                        "assignment": {
                            "question": "updated_question1",
                        },
                    },
                    {
                        "title": "updated_topic_title2",
                        "type": "quiz",
                        "description": "updated_topic_description2",
                        "order": 2,
                        "is_premium": True,
                        "multiple_choice_question": {
                            "question": "updated_question2",
                            "multiple_choice_question_choices": [
                                {"choice": "updated_choice1", "is_correct": False},
                                {"choice": "updated_choice2", "is_correct": False},
                                {"choice": "updated_choice3", "is_correct": False},
                                {"choice": "updated_choice4", "is_correct": True},
                            ],
                        },
                    },
                ],
            },
        ]

        # When
        course_mixin.update_course_with_lectures_and_topics(
            course, course_data, lectures_data
        )

        # Then
        course.refresh_from_db()
        assert course.title == course_data["title"]
        assert course.short_description == course_data["short_description"]
        assert course.description == course_data["description"]
        assert course.category == course_data["category"]
        assert course.skill_level == course_data["skill_level"]
        assert course.price == course_data["price"]
        assert course.lectures.count() == 1
        assert course.lectures.first().topics.count() == 2
        assert course.lectures.first().topics.filter(type="assignment").count() == 1
        assert course.lectures.first().topics.filter(type="quiz").count() == 1
        assert (
            course.lectures.first()
            .topics.filter(type="quiz")
            .first()
            .multiple_choice_question.multiple_choice_question_choices.count()
            == 4
        )
