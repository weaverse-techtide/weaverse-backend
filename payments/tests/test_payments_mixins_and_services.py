import pytest
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied
from unittest.mock import MagicMock, patch
from payments.mixins import (
    GetObjectMixin,
    CartMixin,
    OrderMixin,
    UserBillingAddressMixin,
    PaymentMixin,
)
from payments.services import KakaoPayService
from courses.models import Course
from payments.models import Order, UserBillingAddress


class TestGetObjectMixin:
    @pytest.fixture
    def mixin(self):
        return GetObjectMixin()

    @pytest.mark.django_db
    def test_get_object_or_404_성공(self, mixin, user, course):
        obj = mixin.get_object_or_404(Course.objects.all(), id=course.id)
        assert obj == course

    @pytest.mark.django_db
    def test_get_object_or_404_실패_객체없음(self, mixin):
        with pytest.raises(NotFound):
            mixin.get_object_or_404(Course.objects.all(), id=9999)

    @pytest.mark.django_db
    def test_get_object_or_404_실패_권한없음(self, mixin, user, order):
        mixin.request = MagicMock(user=user)
        other_user = get_user_model().objects.create_user(
            email="other@example.com", password="pass", nickname="othernick"
        )
        order.user = other_user
        order.save()
        with pytest.raises(PermissionDenied):
            mixin.get_object_or_404(Order.objects.all(), id=order.id)


class TestCartMixin:
    @pytest.fixture
    def mixin(self):
        return CartMixin()

    @pytest.mark.django_db
    def test_get_cart_성공(self, mixin, user, cart):
        assert mixin.get_cart(user) == cart

    @pytest.mark.django_db
    def test_get_cart_item_성공(self, mixin, cart, cart_item):
        assert mixin.get_cart_item(cart, id=cart_item.id) == cart_item

    @pytest.mark.django_db
    def test_add_to_cart_성공(self, mixin, cart, course):
        serializer = MagicMock()
        serializer.validated_data = {"course": course}
        serializer.data = {"id": 1, "course": course.id}
        response = mixin.add_to_cart(cart, serializer)
        assert response.status_code == 201
        assert "상품이 장바구니에 추가되었습니다" in response.data["detail"]

    @pytest.mark.django_db
    def test_remove_from_cart_성공(self, mixin, cart_item):
        response = mixin.remove_from_cart(cart_item)
        assert response.status_code == 204


class TestOrderMixin:
    @pytest.fixture
    def mixin(self):
        mixin = OrderMixin()
        mixin.request = MagicMock()
        return mixin

    @pytest.mark.django_db
    def test_get_order_성공(self, mixin, user, order):
        mixin.request.user = user
        assert mixin.get_order(user, id=order.id) == order

    @pytest.mark.django_db
    def test_create_order_from_cart_성공(self, mixin, user, cart, cart_item):
        order_data = mixin.create_order_from_cart(user, cart)
        assert order_data["user_id"] == user.id
        assert len(order_data["order_items"]) == 1

    @pytest.mark.django_db
    def test_create_order_from_cart_실패_장바구니_비어있음(self, mixin, user, cart):
        with pytest.raises(ValidationError):
            mixin.create_order_from_cart(user, cart)


class TestUserBillingAddressMixin:
    @pytest.fixture
    def mixin(self):
        mixin = UserBillingAddressMixin()
        mixin.request = MagicMock()
        return mixin

    @pytest.mark.django_db
    def test_get_billing_address_성공(self, mixin, user, user_billing_address):
        mixin.request.user = user
        assert (
            mixin.get_billing_address(user, id=user_billing_address.id)
            == user_billing_address
        )

    @pytest.mark.django_db
    def test_create_billing_address_성공(self, mixin, user):
        serializer = MagicMock()
        serializer.save.return_value = UserBillingAddress(id=1, user=user)
        response = mixin.create_billing_address(user, serializer)
        assert response.status_code == 201
        assert "청구 주소가 생성되었습니다" in response.data["detail"]


class TestPaymentMixin:
    @pytest.fixture
    def mixin(self):
        mixin = PaymentMixin()
        mixin.request = MagicMock()
        return mixin

    @pytest.mark.django_db
    def test_get_payment_성공(self, mixin, user, payment):
        mixin.request.user = user
        assert mixin.get_payment(user, id=payment.id) == payment

    @pytest.mark.django_db
    def test_validate_order_성공(self, mixin, order):
        mixin.validate_order(order)  # 예외가 발생하지 않아야 함

    @pytest.mark.django_db
    def test_validate_order_실패_주문상태_부적절(self, mixin, completed_order):
        with pytest.raises(ValidationError):
            mixin.validate_order(completed_order)

    @pytest.mark.django_db
    def test_create_payment_성공(self, mixin, order, user, mock_kakao_pay_service):
        mixin.kakao_pay_service = mock_kakao_pay_service
        mock_kakao_pay_service.request_payment.return_value = {"tid": "test_tid"}
        payment, kakao_response = mixin.create_payment(order, user)
        assert payment.order == order
        assert payment.user == user
        assert payment.payment_status == "pending"

    @pytest.mark.django_db
    def test_process_payment_성공(self, mixin, order, payment, mock_kakao_pay_service):
        mixin.kakao_pay_service = mock_kakao_pay_service
        mixin.process_payment(order, payment, "test_pg_token")
        assert payment.payment_status == "completed"
        assert order.order_status == "completed"

    @pytest.mark.django_db
    def test_cancel_payment_성공(self, mixin, order, payment):
        mixin.cancel_payment(order, payment)
        assert payment.payment_status == "cancelled"
        assert order.order_status == "cancelled"

    @pytest.mark.django_db
    def test_refund_payment_성공(
        self, mixin, completed_order, completed_payment, mock_kakao_pay_service
    ):
        mixin.kakao_pay_service = mock_kakao_pay_service
        completed_payment.paid_at = timezone.now()  # 날짜 설정
        mixin.refund_payment(completed_order, completed_payment)
        assert completed_payment.payment_status == "refunded"
        assert completed_order.order_status == "refunded"


class TestKakaoPayService:
    @pytest.fixture
    def service(self):
        return KakaoPayService()

    @pytest.mark.django_db
    def test_request_payment_성공(self, service, order, mock_kakao_pay_settings):
        with patch("requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"tid": "test_tid"}
            response = service.request_payment(order)
        assert response["tid"] == "test_tid"

    @pytest.mark.django_db
    def test_approve_payment_성공(self, service, payment, mock_kakao_pay_settings):
        with patch("requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"amount": {"total": 10000}}
            response = service.approve_payment(payment, "test_pg_token")
        assert response["amount"]["total"] == 10000

    @pytest.mark.django_db
    def test_refund_payment_성공(self, service, payment, mock_kakao_pay_settings):
        with patch("requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"amount": {"total": 10000}}
            response = service.refund_payment(payment)
        assert response["amount"]["total"] == 10000
