from unittest.mock import MagicMock

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from courses.models import Course, Curriculum
from payments.models import (
    Cart,
    CartItem,
    Order,
    OrderItem,
    Payment,
    UserBillingAddress,
)
from payments.services import KakaoPayService


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
def course(staff_user):
    return Course.objects.create(
        title="Test Course",
        author=staff_user,
        price=10000,
        description="This is a test course description",
    )


@pytest.fixture
def curriculum(staff_user):
    return Curriculum.objects.create(
        name="Test Curriculum", price=20000, author=staff_user
    )


@pytest.fixture
def cart_item(cart, course):
    return CartItem.objects.create(cart=cart, course=course, quantity=1)


@pytest.fixture
def order(user):
    return Order.objects.create(user=user, order_status="pending")


@pytest.fixture
def completed_order(user):
    return Order.objects.create(user=user, order_status="completed")


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
def non_default_billing_address(db, user):
    return UserBillingAddress.objects.create(
        user=user,
        country="KR",
        main_address="부산시",
        detail_address="해운대구",
        postal_code="48099",
        is_default=False,
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
def completed_payment(user, completed_order, user_billing_address):
    return Payment.objects.create(
        user=user,
        order=completed_order,
        payment_status="completed",
        amount=10000,
        transaction_id="test_transaction",
        billing_address=user_billing_address,
    )


@pytest.fixture
def completed_payment_with_time(user, completed_order, user_billing_address):
    return Payment.objects.create(
        user=user,
        order=completed_order,
        payment_status="completed",
        amount=10000,
        transaction_id="test_transaction_with_time",
        billing_address=user_billing_address,
        paid_at=timezone.now(),
    )


@pytest.fixture
def mock_kakao_pay_settings(settings):
    settings.KAKAOPAY_SECRET_KEY = "test_secret_key"
    settings.KAKAOPAY_CID = "test_cid"
    settings.BASE_URL = "http://testserver"


@pytest.fixture
def mock_kakao_pay_service():
    return MagicMock(spec=KakaoPayService)


@pytest.fixture
def mock_request():
    request = MagicMock()
    request.user = user()
    return request
