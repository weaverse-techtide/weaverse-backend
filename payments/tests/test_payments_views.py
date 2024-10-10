import pytest
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch
from payments.models import Cart, CartItem, Order, Payment


@pytest.mark.django_db
class TestCartView장바구니뷰:
    def test_장바구니_조회(self, api_client, user, cart, cart_item):
        api_client.force_authenticate(user=user)
        url = reverse("payments:cart-list-create")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["cart_items"]) == 1

    def test_장바구니_상품_추가(self, api_client, user, cart, course):
        api_client.force_authenticate(user=user)
        url = reverse("payments:cart-list-create")
        data = {"course": course.id}
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert CartItem.objects.count() == 1

    def test_장바구니_상품_삭제(self, api_client, user, cart_item):
        api_client.force_authenticate(user=user)
        url = reverse("payments:cart-item-delete", args=[cart_item.id])
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert CartItem.objects.count() == 0


@pytest.mark.django_db
class TestOrderView주문뷰:
    def test_주문_목록_조회(self, api_client, user, order):
        api_client.force_authenticate(user=user)
        url = reverse("payments:order-list-create")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_주문_생성_장바구니에서(self, api_client, user, cart, cart_item):
        api_client.force_authenticate(user=user)
        url = reverse("payments:order-list-create")
        data = {"from_cart": True}
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert Order.objects.count() == 1


@pytest.mark.django_db
class TestPaymentView결제뷰:
    @patch("payments.views.KakaoPayService.request_payment")
    def test_결제_요청(self, mock_request_payment, api_client, user, order):
        mock_request_payment.return_value = {
            "tid": "test_tid",
            "next_redirect_pc_url": "http://test.com",
            "next_redirect_mobile_url": "http://test-mobile.com",
            "next_redirect_app_url": "http://test-app.com",
        }
        api_client.force_authenticate(user=user)
        url = reverse("payments:payment", args=[order.id])
        response = api_client.post(url)
        assert response.status_code == status.HTTP_201_CREATED
        assert Payment.objects.count() == 1

    @patch("payments.views.KakaoPayService.approve_payment")
    def test_결제_승인(self, mock_approve_payment, api_client, user, order, payment):
        mock_approve_payment.return_value = {"approved": True}
        api_client.force_authenticate(user=user)
        url = reverse("payments:payment", args=[order.id])
        response = api_client.get(f"{url}?result=success&pg_token=test_token")
        assert response.status_code == status.HTTP_200_OK
        payment.refresh_from_db()
        assert payment.payment_status == "completed"


@pytest.mark.django_db
class TestReceiptView영수증뷰:
    def test_영수증_목록_조회(self, api_client, user, payment):
        payment.payment_status = "completed"
        payment.save()
        api_client.force_authenticate(user=user)
        url = reverse("payments:receipt-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_영수증_상세_조회(self, api_client, user, payment):
        payment.payment_status = "completed"
        payment.save()
        api_client.force_authenticate(user=user)
        url = reverse("payments:receipt-detail", args=[payment.id])
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["receipt_number"] == f"REC-{payment.id}"
        assert "payment_method" not in response.data["payment_info"]
