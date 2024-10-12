import pytest
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch
from payments.models import CartItem


@pytest.mark.django_db
class Test장바구니뷰:
    def test_장바구니_조회_성공(self, api_client, user, cart_item):
        api_client.force_authenticate(user=user)
        url = reverse("payments:cart-list-create")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["cart_items"]) == 1

    def test_장바구니_아이템_삭제_성공(self, api_client, user, cart_item):
        api_client.force_authenticate(user=user)
        url = reverse("payments:cart-item-delete", args=[cart_item.id])
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class Test주문뷰:
    def test_진행중인_주문_조회_성공(self, api_client, user, order):
        api_client.force_authenticate(user=user)
        url = reverse("payments:order")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["order_status"] == "pending"

    def test_주문_생성_실패_빈_장바구니(self, api_client, user):
        api_client.force_authenticate(user=user)
        url = reverse("payments:order")
        data = {"from_cart": True}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "장바구니가 비어 있습니다" in response.data["detail"]


@pytest.mark.django_db
class Test결제뷰:
    @patch("payments.mixins.KakaoPayService.approve_payment")
    def test_결제_승인_성공(self, mock_approve_payment, api_client, user, payment):
        api_client.force_authenticate(user=user)
        mock_approve_payment.return_value = {"amount": {"total": 10000}}
        url = reverse("payments:payment")
        response = api_client.get(url, {"result": "success", "pg_token": "test_token"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "결제가 성공적으로 완료되었습니다."

    def test_결제_취소(self, api_client, user, payment):
        api_client.force_authenticate(user=user)
        url = reverse("payments:payment")
        response = api_client.get(url, {"result": "cancel"})
        assert response.status_code == status.HTTP_200_OK
        assert "결제 과정이 취소되었습니다" in response.data["detail"]


@pytest.mark.django_db
class Test영수증뷰:
    def test_영수증_목록_조회_성공(self, api_client, user, completed_payment):
        api_client.force_authenticate(user=user)
        url = reverse("payments:receipt-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_영수증_상세_조회_성공(self, api_client, user, completed_payment):
        api_client.force_authenticate(user=user)
        url = reverse("payments:receipt-detail", args=[completed_payment.id])
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == completed_payment.id
