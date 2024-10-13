import pytest

from payments.models import CartItem, OrderItem
from payments.serializers import (
    CartItemSerializer,
    CartSerializer,
    OrderItemSerializer,
    OrderSerializer,
    PaymentSerializer,
    UserBillingAddressSerializer,
)


@pytest.mark.django_db
class TestCartItemSerializer:
    def test_cartitem_serializer_유효성검사(self, cart, course):
        data = {"cart": cart.id, "course": course.id, "quantity": 1}
        serializer = CartItemSerializer(data=data)
        assert serializer.is_valid()

    def test_cartitem_serializer_유효성검사_실패(self, cart, course, curriculum):
        data = {
            "cart": cart.id,
            "course": course.id,
            "curriculum": curriculum.id,
            "quantity": 1,
        }
        serializer = CartItemSerializer(data=data)
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors


@pytest.mark.django_db
class TestCartSerializer:
    def test_cart_serializer(self, cart, course):
        CartItem.objects.create(cart=cart, course=course, quantity=1)
        serializer = CartSerializer(cart)
        assert serializer.data["get_total_items"] == 1
        assert serializer.data["get_total_price"] == course.price


@pytest.mark.django_db
class TestOrderItemSerializer:
    def test_orderitem_serializer_유효성검사(self, order, course):
        data = {"order": order.id, "course": course.id, "quantity": 1}
        serializer = OrderItemSerializer(data=data)
        assert serializer.is_valid()

    # def test_orderitem_serializer_유효성검사_실패(self, order, course, curriculum):
    #     data = {
    #         "order": order.id,
    #         "course": course.id,
    #         "curriculum": curriculum.id,
    #         "quantity": 1,
    #     }
    #     serializer = OrderItemSerializer(data=data)
    #     assert not serializer.is_valid()
    #     assert "non_field_errors" in serializer.errors


@pytest.mark.django_db
class TestOrderSerializer:
    def test_order_serializer(self, order, course):
        OrderItem.objects.create(order=order, course=course, quantity=1)
        serializer = OrderSerializer(order)
        assert serializer.data["get_total_items"] == 1
        assert serializer.data["get_total_price"] == course.price


@pytest.mark.django_db
class TestUserBillingAddressSerializer:
    def test_user_billing_address_serializer(self, user_billing_address):
        serializer = UserBillingAddressSerializer(user_billing_address)
        assert serializer.data["country"] == "대한민국"
        assert serializer.data["main_address"] == "서울특별시 강남구"
        assert serializer.data["is_default"] == True


@pytest.mark.django_db
class TestPaymentSerializer:
    def test_payment_serializer(self, payment):
        serializer = PaymentSerializer(payment)
        assert serializer.data["payment_status"] == "pending"
        assert serializer.data["amount"] == 10000
        assert serializer.data["transaction_id"] == "test_transaction"
