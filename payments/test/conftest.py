import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.conf import settings

from payments.models import (
    Cart,
    Order,
    Payment,
    UserBillingAddress,
    CartItem,
    OrderItem,
)
from courses.models import Course, Curriculum


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    User = get_user_model()
    return User.objects.create_user(
        email="test@example.com", password="testpass123", nickname="testnick"
    )


@pytest.fixture
def staff_user():
    User = get_user_model()
    return User.objects.create_user(
        email="staff@example.com",
        password="staffpass123",
        is_staff=True,
        nickname="staffnick",
    )


@pytest.fixture
def cart(user):
    return Cart.objects.create(user=user)


@pytest.fixture
def course():
    return Course.objects.create(
        title="Test Course",
        price=10000,
        description="This is a test course description",  # 추가된 부분
    )


@pytest.fixture
def curriculum():
    return Curriculum.objects.create(name="Test Curriculum", price=20000)


@pytest.fixture
def cart_item(cart, course):
    return CartItem.objects.create(cart=cart, course=course, quantity=1)


@pytest.fixture
def order(user):
    return Order.objects.create(user=user, order_status="pending")


@pytest.fixture
def order_item(order, course):
    return OrderItem.objects.create(order=order, course=course, quantity=1)


@pytest.fixture
def user_billing_address(user):
    return UserBillingAddress.objects.create(
        user=user,
        country="대한민국",
        main_address="서울특별시 강남구",
        detail_address="테헤란로 123",
        postal_code="06234",
        is_default=True,
    )


@pytest.fixture
def payment(user, order, user_billing_address):
    return Payment.objects.create(
        user=user,
        order=order,
        payment_status="pending",
        amount=10000,
        transaction_id="test_transaction",
        billing_address=user_billing_address,
    )


@pytest.fixture
def mock_kakao_pay_settings(settings):
    settings.KAKAOPAY_SECRET_KEY = "test_secret_key"
    settings.KAKAOPAY_CID = "test_cid"
    settings.BASE_URL = "http://testserver"
