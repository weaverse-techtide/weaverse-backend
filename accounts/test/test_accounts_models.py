import pytest
from accounts.models import CustomUser
from django.core.exceptions import ValidationError


@pytest.mark.django_db
def test_create_user():
    user = CustomUser.objects.create_user(
        email="test@example.com", password="testpass123"
    )
    assert user.email == "test@example.com"
    assert user.is_active
    assert not user.is_staff
    assert not user.is_superuser


@pytest.mark.django_db
def test_create_superuser():
    admin = CustomUser.objects.create_superuser(
        email="admin@example.com", password="adminpass123"
    )
    assert admin.email == "admin@example.com"
    assert admin.is_active
    assert admin.is_staff
    assert admin.is_superuser


@pytest.mark.django_db
def test_user_str():
    user = CustomUser.objects.create_user(
        email="test@example.com", password="testpass123"
    )
    assert str(user) == "test@example.com"


@pytest.mark.django_db
def test_clean_method():
    user = CustomUser(password="testpass123")
    with pytest.raises(ValidationError):
        user.clean()
