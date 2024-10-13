import pytest
from django.utils import timezone
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch


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
    @patch("payments.mixins.KakaoPayService.request_payment")
    def test_결제_요청(self, mock_request_payment, api_client, user, order):
        mock_request_payment.return_value = {
            "next_redirect_pc_url": "http://test-redirect-url.com",
            "next_redirect_mobile_url": "http://test-redirect-url.com",
            "next_redirect_app_url": "http://test-redirect-url.com",
            "tid": "test_transaction_id",
        }
        api_client.force_authenticate(user=user)
        url = reverse("payments:payment")
        response = api_client.post(url)
        print(f"\n결제 요청 테스트")
        print(f"URL: {url}")
        print(f"응답 상태 코드: {response.status_code}")
        print(f"응답 데이터: {response.data}")
        assert response.status_code == status.HTTP_201_CREATED
        assert "payment" in response.data
        assert "next_redirect_pc_url" in response.data

    @patch("payments.mixins.KakaoPayService.approve_payment")
    def test_결제_승인_성공(self, mock_approve_payment, api_client, user, payment):
        mock_approve_payment.return_value = {"amount": {"total": 10000}}
        api_client.force_authenticate(user=user)
        url = reverse("payments:payment")
        response = api_client.get(url, {"result": "success", "pg_token": "test_token"})
        print(f"\n결제 승인 테스트")
        print(f"URL: {url}")
        print(f"응답 상태 코드: {response.status_code}")
        print(f"응답 데이터: {response.data}")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "결제가 성공적으로 완료되었습니다."

    def test_결제_취소(self, api_client, user, payment):
        api_client.force_authenticate(user=user)
        url = reverse("payments:payment")
        response = api_client.get(url, {"result": "cancel"})
        print(f"\n결제 취소 테스트")
        print(f"URL: {url}")
        print(f"응답 상태 코드: {response.status_code}")
        print(f"응답 데이터: {response.data}")
        assert response.status_code == status.HTTP_200_OK
        assert "결제 과정이 취소되었습니다" in response.data["detail"]

    @patch("payments.mixins.KakaoPayService.refund_payment")
    def test_결제_환불(self, mock_refund_payment, api_client, user, completed_payment):
        mock_refund_payment.return_value = {"status": "CANCEL_PAYMENT"}
        completed_payment.paid_at = timezone.now()
        completed_payment.save()
        api_client.force_authenticate(user=user)
        url = reverse("payments:payment-cancel", args=[completed_payment.order.id])
        response = api_client.delete(url)
        print(f"\n결제 환불 테스트")
        print(f"URL: {url}")
        print(f"응답 상태 코드: {response.status_code}")
        print(f"응답 데이터: {response.data}")
        assert response.status_code == status.HTTP_200_OK
        assert "결제가 성공적으로 환불되었습니다" in response.data["detail"]


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
