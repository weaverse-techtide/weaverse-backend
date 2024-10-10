from django.conf import settings
import requests


class KakaoPayService:
    """
    카카오페이 결제 서비스를 처리하는 클래스입니다.
    """

    def request_payment(self, order):
        """
        주어진 주문에 대해 카카오페이 결제 요청을 보냅니다.

        Args:
            order: 결제를 요청할 주문 객체

        Returns:
            dict: 카카오페이 결제 요청에 대한 응답 데이터
        """

        url = "https://open-api.kakaopay.com/online/v1/payment/ready"
        headers = {
            "Authorization": f"SECRET_KEY {settings.KAKAOPAY_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        base_url = settings.BASE_URL.strip("'").split("#")[0].strip()
        payload = {
            "cid": settings.KAKAOPAY_CID,
            "partner_order_id": str(order.id),
            "partner_user_id": str(order.user.id),
            "item_name": f"Order #{order.id}",
            "quantity": order.get_total_items(),
            "total_amount": order.get_total_price(),
            "tax_free_amount": 0,
            "approval_url": f"{base_url}/api/payments/{order.id}/?result=success",
            "cancel_url": f"{base_url}/api/payments/{order.id}/?result=cancel",
            "fail_url": f"{base_url}/api/payments/{order.id}/?result=fail",
        }

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            raise Exception(f"카카오페이 결제 요청 실패: {response.text}")

        return response.json()

    def approve_payment(self, payment, pg_token):
        """
        주어진 주문에 대해 카카오페이 결제를 승인합니다.

        Args:
            order: 결제를 승인할 주문 객체
            pg_token: 결제 승인 토큰

        Returns:
            dict: 카카오페이 결제 승인에 대한 응답 데이터
        """

        url = "https://open-api.kakaopay.com/online/v1/payment/approve"
        headers = {
            "Authorization": f"SECRET_KEY {settings.KAKAOPAY_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "cid": settings.KAKAOPAY_CID,
            "tid": payment.transaction_id,
            "partner_order_id": str(payment.order.id),
            "partner_user_id": str(payment.user.id),
            "pg_token": pg_token,
        }

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            raise Exception("카카오페이 결제 승인 실패")

        return response.json()

    def cancel_payment(self, payment):
        """
        주어진 주문에 대해 카카오페이 결제를 취소합니다.

        Args:
            order: 결제를 취소할 주문 객체

        Returns:
            dict: 카카오페이 결제 취소에 대한 응답 데이터
        """

        url = "https://open-api.kakaopay.com/online/v1/payment/cancel"
        headers = {
            "Authorization": f"SECRET_KEY {settings.KAKAOPAY_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "cid": settings.KAKAOPAY_CID,
            "tid": payment.transaction_id,
            "cancel_amount": payment.amount,
            "cancel_tax_free_amount": 0,
        }

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            raise Exception("카카오페이 결제 취소 실패")

        return response.json()
