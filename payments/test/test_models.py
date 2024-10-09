import pytest
from payments.models import (
    Cart,
    CartItem,
    Order,
    OrderItem,
    Payment,
    UserBillingAddress,
)


@pytest.mark.django_db
class TestCart:
    def test_cart_생성(self, user):
        cart = Cart.objects.create(user=user)
        assert cart.user == user
        assert cart.total_items() == 0
        assert cart.total_price() == 0

    def test_cart_total_items_and_price(self, cart, course, curriculum):
        CartItem.objects.create(cart=cart, course=course, quantity=1)
        CartItem.objects.create(cart=cart, curriculum=curriculum, quantity=1)
        assert cart.total_items() == 2
        assert cart.total_price() == course.price + curriculum.price


@pytest.mark.django_db
class TestOrder:
    def test_order_생성(self, user):
        order = Order.objects.create(user=user, order_status="pending")
        assert order.user == user
        assert order.order_status == "pending"
        assert order.total_items() == 0
        assert order.total_price() == 0

    def test_order_total_items_and_price(self, order, course, curriculum):
        OrderItem.objects.create(order=order, course=course, quantity=1)
        OrderItem.objects.create(order=order, curriculum=curriculum, quantity=1)
        assert order.total_items() == 2
        assert order.total_price() == course.price + curriculum.price


@pytest.mark.django_db
class TestUserBillingAddress:
    def test_user_billing_address_생성(self, user):
        address = UserBillingAddress.objects.create(
            user=user,
            country="대한민국",
            main_address="서울특별시 강남구",
            detail_address="테헤란로 123",
            postal_code="06234",
            is_default=True,
        )
        assert address.user == user
        assert address.is_default == True

    def test_user_billing_address_default_설정(self, user):
        address1 = UserBillingAddress.objects.create(
            user=user,
            country="대한민국",
            main_address="서울특별시 강남구",
            detail_address="테헤란로 123",
            postal_code="06234",
            is_default=True,
        )
        address2 = UserBillingAddress.objects.create(
            user=user,
            country="대한민국",
            main_address="서울특별시 서초구",
            detail_address="반포대로 123",
            postal_code="06548",
            is_default=True,
        )
        address1.refresh_from_db()
        assert address1.is_default == False
        assert address2.is_default == True


@pytest.mark.django_db
class TestPayment:
    def test_payment_생성(self, user, order, user_billing_address):
        payment = Payment.objects.create(
            user=user,
            order=order,
            payment_status="pending",
            amount=10000,
            transaction_id="test_transaction",
            billing_address=user_billing_address,
        )
        assert payment.user == user
        assert payment.order == order
        assert payment.payment_status == "pending"
        assert payment.amount == 10000
        assert payment.transaction_id == "test_transaction"
        assert payment.billing_address == user_billing_address

    def test_payment_default_billing_address(self, user, order):
        payment = Payment.objects.create(
            user=user,
            order=order,
            payment_status="pending",
            amount=10000,
            transaction_id="test_transaction",
        )
        assert payment.billing_address is None

        default_address = UserBillingAddress.objects.create(
            user=user,
            country="대한민국",
            main_address="서울특별시 강남구",
            detail_address="테헤란로 123",
            postal_code="06234",
            is_default=True,
        )
        payment.save()
        payment.refresh_from_db()
        assert payment.billing_address == default_address
