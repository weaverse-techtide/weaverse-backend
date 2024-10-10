import pytest
from django.utils import timezone

from courses.models import Course, Curriculum


@pytest.mark.django_db
def test_course_생성(create_staff_user):
    # Given
    curriculum = Curriculum.objects.create(
        name="Test Curriculum",
        description="Test Description",
        price=1000,
        author=create_staff_user,
    )

    # When
    course = Course.objects.create(
        curriculum=curriculum,
        title="Test Course",
        short_description="Short Description",
        description={"content": "Detailed Description"},
        category="Python",
        skill_level="beginner",
        price=500,
        author=create_staff_user,
    )

    # Then
    assert course.title == "Test Course"
    assert course.short_description == "Short Description"
    assert course.description == {"content": "Detailed Description"}
    assert course.category == "Python"
    assert course.skill_level == "beginner"
    assert course.price == 500
    assert course.curriculum == curriculum
    assert course.created_at <= timezone.now()
    assert course.updated_at <= timezone.now()


@pytest.mark.django_db
def test_course_업데이트(create_staff_user):
    # Given
    curriculum = Curriculum.objects.create(
        name="Test Curriculum",
        description="Test Description",
        price=1000,
        author=create_staff_user,
    )
    course = Course.objects.create(
        curriculum=curriculum,
        title="Test Course",
        short_description="Short Description",
        description={"content": "Detailed Description"},
        category="Python",
        skill_level="beginner",
        price=500,
        author=create_staff_user,
    )

    # When
    course.update(
        title="Updated Course",
        short_description="Updated Short Description",
        description={"content": "Updated Detailed Description"},
        category="Django",
        skill_level="intermediate",
        price=700,
    )

    # Then
    updated_course = Course.objects.get(id=course.id)
    assert updated_course.title == "Updated Course"
    assert updated_course.short_description == "Updated Short Description"
    assert updated_course.description == {"content": "Updated Detailed Description"}
    assert updated_course.category == "Django"
    assert updated_course.skill_level == "intermediate"
    assert updated_course.price == 700


@pytest.mark.django_db
def test_course_업데이트_course의_없는_필드는_무시된다(create_staff_user):
    # Given
    curriculum = Curriculum.objects.create(
        name="Test Curriculum",
        description="Test Description",
        price=1000,
        author=create_staff_user,
    )
    course = Course.objects.create(
        curriculum=curriculum,
        title="Test Course",
        short_description="Short Description",
        description={"content": "Detailed Description"},
        category="Python",
        skill_level="beginner",
        price=500,
        author=create_staff_user,
    )

    # When
    course.update(title="Updated Course", not_exist_field="Not Exist Field")

    # Then
    updated_course = Course.objects.get(id=course.id)
    assert updated_course.title == "Updated Course"
    assert updated_course.short_description == "Short Description"
    assert updated_course.description == {"content": "Detailed Description"}
    assert updated_course.category == "Python"
    assert updated_course.skill_level == "beginner"
    assert updated_course.price == 500


@pytest.mark.django_db
def test_course_업데이트_특정_필드만_업데이트(create_staff_user):
    # Given
    curriculum = Curriculum.objects.create(
        name="Test Curriculum",
        description="Test Description",
        price=1000,
        author=create_staff_user,
    )
    course = Course.objects.create(
        curriculum=curriculum,
        title="Test Course",
        short_description="Short Description",
        description={"content": "Detailed Description"},
        category="Python",
        skill_level="beginner",
        price=500,
        author=create_staff_user,
    )

    # When
    course.update(title="Updated Course", lectures=[{"title": "Test Lecture"}])

    # Then
    updated_course = Course.objects.get(id=course.id)
    assert updated_course.title == "Updated Course"
    assert updated_course.short_description == "Short Description"
    assert updated_course.description == {"content": "Detailed Description"}
    assert updated_course.category == "Python"
    assert updated_course.skill_level == "beginner"
    assert updated_course.price == 500
    assert updated_course.lectures.count() == 0
