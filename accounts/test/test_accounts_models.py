import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


@pytest.mark.django_db
class TestCustomUser:

    # Given: CustomUser 모델이 존재할 때
    # When: 일반 사용자를 생성하면
    # Then: 사용자가 정상적으로 생성되어야 합니다.
    def test_user_생성(self):
        user = User.objects.create_user(
            email="test@example.com", password="testpassword", nickname="testnick"
        )
        assert user.email == "test@example.com"
        assert user.nickname == "testnick"
        assert not user.is_staff
        assert not user.is_superuser

    # Given: CustomUser 모델이 존재할 때
    # When: 스태프 사용자를 생성하면
    # Then: 스태프 권한을 가진 사용자가 정상적으로 생성되어야 합니다.
    def test_staff_생성(self):
        staff = User.objects.create_staff(
            email="staff@example.com", password="staffpassword", nickname="staffnick"
        )
        assert staff.email == "staff@example.com"
        assert staff.nickname == "staffnick"
        assert staff.is_staff
        assert not staff.is_superuser

    # Given: CustomUser 모델이 존재할 때
    # When: 슈퍼유저를 생성하면
    # Then: 관리자 권한을 가진 사용자가 정상적으로 생성되어야 한다.
    def test_superuser_생성(self):
        admin = User.objects.create_superuser(
            email="admin@example.com", password="adminpassword", nickname="adminnick"
        )
        assert admin.email == "admin@example.com"
        assert admin.nickname == "adminnick"
        assert admin.is_staff
        assert admin.is_superuser

    # Given: CustomUser 모델이 존재할 때
    # When: 이메일 없이 사용자를 생성하려고 하면
    # Then: ValueError가 발생해야 한다.
    def test_user_생성_without_이메일(self):
        with pytest.raises(ValueError):
            User.objects.create_user(
                email="", password="testpassword", nickname="testnick"
            )

    # Given: CustomUser 모델이 존재할 때
    # When: 닉네임 없이 사용자를 생성하려고 하면
    # Then: ValueError가 발생해야 한다.
    def test_user_생성_withdout_닉네임(self):
        with pytest.raises(ValueError):
            User.objects.create_user(
                email="test@example.com", password="testpassword", nickname=""
            )

    # Given: CustomUser 모델이 존재할 때
    # When: is_staff=False로 스태프를 생성하려고 하면
    # Then: ValueError가 발생해야 한다.
    def test_staff_생성_is_staff를_false값으로(self):
        with pytest.raises(ValueError):
            User.objects.create_staff(
                email="staff@example.com",
                password="staffpassword",
                nickname="staffnick",
                is_staff=False,
            )

    # Given: CustomUser 모델이 존재할 때
    # When: is_superuser=False로 슈퍼유저를 생성하려고 하면
    # Then: ValueError가 발생해야 한다.
    def test_superuser_생성_is_superuser를_false값으로(self):
        with pytest.raises(ValueError):
            User.objects.create_superuser(
                email="admin@example.com",
                password="adminpassword",
                nickname="adminnick",
                is_superuser=False,
            )

    # Given: CustomUser 모델이 존재하고 튜터와 학생이 생성되어 있을 때
    # When: 튜터에게 학생을 할당하면
    # Then: 튜터-학생 관계가 정상적으로 설정되어야 한다.
    def test_tutor에게_student를_할당해서_관계_생성(self):
        tutor = User.objects.create_staff(
            email="tutor@example.com", password="tutorpassword", nickname="tutornick"
        )
        student = User.objects.create_user(
            email="student@example.com",
            password="studentpassword",
            nickname="studentnick",
        )
        tutor.students.add(student)
        assert student in tutor.students.all()
        assert tutor in student.tutors.all()

    # Given: CustomUser 모델이 존재하고 사용자가 생성되어 있을 때
    # When: 사용자의 문자열 표현을 요청하면
    # Then: 사용자의 이메일이 반환되어야 한다.
    def test_user_str_representation_출력(self):
        user = User.objects.create_user(
            email="test@example.com", password="testpassword", nickname="testnick"
        )
        assert str(user) == "test@example.com"

    # Given: CustomUser 모델이 존재할 때
    # When: 동일한 이메일로 두 명의 사용자를 생성하려고 하면
    # Then: IntegrityError가 발생해야 한다. (pytest-django에서는 TransactionManagement)
    def test_email_기본키_constraint_만족(self):
        User.objects.create_user(
            email="test@example.com", password="testpassword1", nickname="testnick1"
        )
        with pytest.raises(Exception):
            User.objects.create_user(
                email="test@example.com", password="testpassword2", nickname="testnick2"
            )

    # Given: CustomUser 모델이 존재할 때
    # When: 동일한 닉네임으로 두 명의 사용자를 생성하려고 하면
    # Then: IntegrityError가 발생해야 한다
    def test_nickname_후보키_constraint_만족(self):
        User.objects.create_user(
            email="test1@example.com", password="testpassword1", nickname="testnick"
        )
        with pytest.raises(Exception):
            User.objects.create_user(
                email="test2@example.com", password="testpassword2", nickname="testnick"
            )
