import requests
from django.conf import settings


class KakaoPayService:
    """
    카카오페이 결제 서비스를 처리하는 클래스입니다.
    """

    def request_payment(self, order):
        """
        주어진 주문에 대해 카카오페이 결제 요청을 보냅니다.
        """
        url = "https://open-api.kakaopay.com/online/v1/payment/ready"
        headers = self._get_headers()
        base_url = settings.BASE_URL.strip("'").split("#")[0].strip()

        payment_request = {
            "cid": settings.KAKAOPAY_CID,
            "partner_order_id": str(order.id),
            "partner_user_id": str(order.user.id),
            "item_name": f"Order #{order.id}",
            "quantity": order.get_total_items(),
            "total_amount": int(order.get_total_price()),
            "tax_free_amount": 0,
            "approval_url": f"{base_url}payments/?result=success",
            "cancel_url": f"{base_url}api/payments/{order.id}/?result=cancel",
            "fail_url": f"{base_url}api/payments/{order.id}/?result=fail",
        }

        response = requests.post(url, json=payment_request, headers=headers)
        if response.status_code != 200:
            raise Exception(f"카카오페이 결제 요청 실패: {response.text}")

        return response.json()

    def approve_payment(self, payment, pg_token):
        """
        주어진 주문에 대해 카카오페이 결제를 승인합니다.
        """
        url = "https://open-api.kakaopay.com/online/v1/payment/approve"
        headers = self._get_headers()

        approval_request = {
            "cid": settings.KAKAOPAY_CID,
            "tid": payment.transaction_id,
            "partner_order_id": str(payment.order.id),
            "partner_user_id": str(payment.user.id),
            "pg_token": pg_token,
        }

        response = requests.post(url, json=approval_request, headers=headers)
        if response.status_code != 200:
            raise Exception("카카오페이 결제 승인 실패")

        return response.json()

    def refund_payment(self, payment):
        """
        주어진 주문에 대해 카카오페이 결제를 환불합니다.
        """
        url = "https://open-api.kakaopay.com/online/v1/payment/cancel"
        headers = self._get_headers()

        refund_request = {
            "cid": settings.KAKAOPAY_CID,
            "tid": payment.transaction_id,
            "cancel_amount": payment.amount,
            "cancel_tax_free_amount": 0,
        }

        response = requests.post(url, json=refund_request, headers=headers)
        if response.status_code != 200:
            raise Exception("카카오페이 결제 환불 실패")

        return response.json()

    def _get_headers(self):
        return {
            "Authorization": f"SECRET_KEY {settings.KAKAOPAY_SECRET_KEY}",
            "Content-Type": "application/json",
        }
