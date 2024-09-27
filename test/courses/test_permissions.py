import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory

from courses.permissions import IsStaffOrReadOnly


@pytest.mark.django_db
class TestIsStaffOrReadOnly:

    def test_누가나_GET_권한을가진다(self):
        # Given
        permission = IsStaffOrReadOnly()
        factory = APIRequestFactory()
        request = factory.get("/fake-url/")

        # When, Then
        assert permission.has_permission(request, None) is True

    def test_누가나_HEAD_권한을가진다(self):
        # Given
        permission = IsStaffOrReadOnly()
        factory = APIRequestFactory()
        request = factory.head("/fake-url/")

        # When, Then
        assert permission.has_permission(request, None) is True

    def test_누가나_OPTIONS_권한을가진다(self):
        # Given
        permission = IsStaffOrReadOnly()
        factory = APIRequestFactory()
        request = factory.options("/fake-url/")

        # When, Then
        assert permission.has_permission(request, None) is True

    def test_staff는_POST_권한을가진다(self):
        # Given
        permission = IsStaffOrReadOnly()
        factory = APIRequestFactory()
        request = factory.post("/fake-url/")
        request.user = User(is_staff=True)

        # When, Then
        assert permission.has_permission(request, None) is True

    def test_staff는_PUT_권한을가진다(self):
        # Given
        permission = IsStaffOrReadOnly()
        factory = APIRequestFactory()
        request = factory.put("/fake-url/")
        request.user = User(is_staff=True)

        # When, Then
        assert permission.has_permission(request, None) is True

    def test_staff는_PATCH_권한을가진다(self):
        # Given
        permission = IsStaffOrReadOnly()
        factory = APIRequestFactory()
        request = factory.patch("/fake-url/")
        request.user = User(is_staff=True)

        # When, Then
        assert permission.has_permission(request, None) is True

    def test_staff는_DELETE_권한을가진다(self):
        # Given
        permission = IsStaffOrReadOnly()
        factory = APIRequestFactory()
        request = factory.delete("/fake-url/")
        request.user = User(is_staff=True)

        # When, Then
        assert permission.has_permission(request, None) is True

    def test_staff가아닌사람은_POST_권한이없다(self):
        # Given
        permission = IsStaffOrReadOnly()
        factory = APIRequestFactory()
        request = factory.post("/fake-url/")
        request.user = User(is_staff=False)

        # When, Then
        assert permission.has_permission(request, None) is False

    def test_staff가아닌사람은_PUT_권한이없다(self):
        # Given
        permission = IsStaffOrReadOnly()
        factory = APIRequestFactory()
        request = factory.put("/fake-url/")
        request.user = User(is_staff=False)

        # When, Then
        assert permission.has_permission(request, None) is False

    def test_staff가아닌사람은_PATCH_권한이없다(self):
        # Given
        permission = IsStaffOrReadOnly()
        factory = APIRequestFactory()
        request = factory.patch("/fake-url/")
        request.user = User(is_staff=False)

        # When, Then
        assert permission.has_permission(request, None) is False

    def test_staff가아닌사람은_DELETE_권한이없다(self):
        # Given
        permission = IsStaffOrReadOnly()
        factory = APIRequestFactory()
        request = factory.delete("/fake-url/")
        request.user = User(is_staff=False)

        # When, Then
        assert permission.has_permission(request, None) is False
