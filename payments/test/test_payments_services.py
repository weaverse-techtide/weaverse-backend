import pytest
from unittest.mock import patch, MagicMock
from payments.services import KakaoPayService


@pytest.mark.django_db
class TestKakaoPayService카카오페이서비스:
    @patch("payments.services.requests.post")
    def test_결제_요청(self, mock_post, order, mock_kakao_pay_settings):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"tid": "test_tid"}
        mock_post.return_value = mock_response

        service = KakaoPayService()
        result = service.request_payment(order)

        assert result["tid"] == "test_tid"
        mock_post.assert_called_once()

    @patch("payments.services.requests.post")
    def test_결제_승인(self, mock_post, payment, mock_kakao_pay_settings):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"approved": True}
        mock_post.return_value = mock_response

        service = KakaoPayService()
        result = service.approve_payment(payment, "test_pg_token")

        assert result["approved"] == True
        mock_post.assert_called_once()

    @patch("payments.services.requests.post")
    def test_결제_취소(self, mock_post, payment, mock_kakao_pay_settings):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"canceled_amount": {"total": 10000}}
        mock_post.return_value = mock_response

        service = KakaoPayService()
        result = service.cancel_payment(payment)

        assert result["canceled_amount"]["total"] == 10000
        mock_post.assert_called_once()

    @patch("payments.services.requests.post")
    def test_결제_요청_실패(self, mock_post, order, mock_kakao_pay_settings):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        service = KakaoPayService()
        with pytest.raises(Exception, match="카카오페이 결제 요청 실패: Bad Request"):
            service.request_payment(order)

    @patch("payments.services.requests.post")
    def test_결제_승인_실패(self, mock_post, payment, mock_kakao_pay_settings):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        service = KakaoPayService()
        with pytest.raises(Exception, match="카카오페이 결제 승인 실패"):
            service.approve_payment(payment, "test_pg_token")

    @patch("payments.services.requests.post")
    def test_결제_취소_실패(self, mock_post, payment, mock_kakao_pay_settings):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        service = KakaoPayService()
        with pytest.raises(Exception, match="카카오페이 결제 취소 실패"):
            service.cancel_payment(payment)
