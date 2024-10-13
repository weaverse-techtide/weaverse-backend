from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.response import Response

from .models import Cart, CartItem, Order, Payment, UserBillingAddress
from .services import KakaoPayService


class GetObjectMixin:
    def get_object_or_404(self, queryset, *filter_args, **filter_kwargs):
        try:
            obj = queryset.get(*filter_args, **filter_kwargs)
            if hasattr(obj, "user") and obj.user != self.request.user:
                raise PermissionDenied("이 객체에 접근할 권한이 없습니다.")
            return obj
        except queryset.model.DoesNotExist:
            verbose_name = getattr(
                queryset.model._meta, "verbose_name", queryset.model.__name__
            )
            raise NotFound(detail=f"{verbose_name}을(를) 찾을 수 없습니다.")


class CartMixin(GetObjectMixin):
    def get_cart(self, user):
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    def get_cart_item(self, cart, **kwargs):
        return self.get_object_or_404(CartItem.objects.filter(cart=cart), **kwargs)

    @transaction.atomic
    def add_to_cart(self, cart, serializer):
        existing_item = CartItem.objects.filter(
            cart=cart,
            curriculum=serializer.validated_data.get("curriculum"),
            course=serializer.validated_data.get("course"),
        ).first()

        if existing_item:
            return Response(
                {"detail": "이 상품은 이미 장바구니에 있습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            serializer.save(cart=cart)
            return Response(
                {
                    "detail": "상품이 장바구니에 추가되었습니다.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

    def remove_from_cart(self, cart_item):
        cart_item.delete()
        return Response(
            {"detail": "상품이 장바구니에서 삭제되었습니다."},
            status=status.HTTP_204_NO_CONTENT,
        )


class OrderMixin(GetObjectMixin):
    def get_order(self, user, **kwargs):
        return self.get_object_or_404(Order.objects.filter(user=user), **kwargs)

    def create_order_from_cart(self, user, cart):
        if not cart.cart_items.exists():
            raise ValidationError("장바구니가 비어있습니다.")

        if cart.get_total_price() > 50000:
            raise ValidationError("상품의 총 가격이 50,000원을 초과할 수 없습니다.")

        order_items = [
            {
                "curriculum_id": item.curriculum.id if item.curriculum else None,
                "course_id": item.course.id if item.course else None,
                "quantity": item.quantity,
                "price": item.get_price(),
            }
            for item in cart.cart_items.all()
        ]

        return {
            "user_id": user.id,
            "order_status": "pending",
            "order_items": order_items,
        }

    def create_new_order(self, user, order_data):
        if not order_data.get("order_items"):
            raise ValidationError("주문 항목이 없습니다.")

        return {
            "user_id": user.id,
            "order_status": "pending",
            "order_items": order_data.get("order_items", []),
        }


class UserBillingAddressMixin(GetObjectMixin):
    def get_billing_address(self, user, **kwargs):
        return self.get_object_or_404(
            UserBillingAddress.objects.filter(user=user), **kwargs
        )

    def create_billing_address(self, user, serializer):
        instance = serializer.save(user=user, is_default=True)
        UserBillingAddress.objects.filter(user=user, is_default=True).exclude(
            pk=instance.pk
        ).update(is_default=False)
        return Response(
            {"detail": "청구 주소가 생성되었습니다."}, status=status.HTTP_201_CREATED
        )

    def update_billing_address(self, instance, serializer):
        serializer.save()
        return Response(
            {"detail": "청구 주소가 수정되었습니다.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def delete_billing_address(self, instance):
        instance.delete()
        return Response(
            {"detail": "청구 주소가 삭제되었습니다."},
            status=status.HTTP_204_NO_CONTENT,
        )


class PaymentMixin(GetObjectMixin):
    kakao_pay_service = KakaoPayService()

    def get_payment(self, user, select_for_update=False, **kwargs):
        queryset = Payment.objects.filter(user=user)
        if select_for_update:
            queryset = queryset.select_for_update()
        return self.get_object_or_404(queryset, **kwargs)

    def validate_order(self, order):
        if order.order_status != "pending":
            raise ValidationError("결제 가능한 상태의 주문이 아닙니다.")
        if order.get_total_price() > 50000:
            raise ValidationError("결제 금액이 50,000원을 초과할 수 없습니다.")

    def create_payment(self, order, user):
        self.validate_order(order)

        existing_payments = Payment.objects.filter(
            order=order, payment_status="pending"
        )
        if existing_payments.exists():
            # 모든 기존 pending payment를 취소 처리
            existing_payments.update(payment_status="cancelled")

        try:
            kakao_response = self.kakao_pay_service.request_payment(order)
        except Exception as e:
            raise ValidationError(
                "결제 요청 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."
            )

        billing_address = UserBillingAddress.objects.filter(
            user=user, is_default=True
        ).first()

        payment = Payment.objects.create(
            order=order,
            user=user,
            payment_status="pending",
            amount=order.get_total_price(),
            transaction_id=kakao_response["tid"],
            billing_address=billing_address,
        )

        return payment, kakao_response

    def process_payment(self, order, payment, pg_token):
        try:
            self.kakao_pay_service.approve_payment(payment, pg_token)
        except Exception as e:
            payment.payment_status = "failed"
            payment.save()
            raise ValidationError(
                "결제 승인 중 오류가 발생했습니다. 고객센터로 문의해 주세요."
            )

        payment.payment_status = "completed"
        payment.paid_at = timezone.now()
        payment.save()
        order.order_status = "completed"
        order.save()

        for order_item in order.order_items.all():
            order_item.save()

    def cancel_payment(self, order, payment):
        payment.payment_status = "cancelled"
        payment.cancelled_at = timezone.now()
        payment.save()
        order.order_status = "cancelled"
        order.save()

    def fail_payment(self, payment):
        payment.payment_status = "failed"
        payment.save()

    def refund_payment(self, order, payment):
        if order.order_status != "completed":
            raise ValidationError("완료된 주문만 취소할 수 있습니다.")

        if not payment or payment.payment_status != "completed":
            raise ValidationError("해당 주문에 대한 완료된 결제를 찾을 수 없습니다.")

        if payment.paid_at is None:
            raise ValidationError("결제 완료 시간이 기록되지 않았습니다.")

        if timezone.now() - payment.paid_at > timezone.timedelta(days=7):
            raise ValidationError("결제 후 7일이 지난 주문은 환불할 수 없습니다.")

        try:
            self.kakao_pay_service.refund_payment(payment)
        except Exception as e:
            raise ValidationError(
                "결제 취소 중 오류가 발생했습니다. 고객센터로 문의해 주세요."
            )

        payment.payment_status = "refunded"
        payment.cancelled_at = timezone.now()
        payment.save()
        order.order_status = "refunded"
        order.save()

        for order_item in order.order_items.all():
            order_item.expiry_date = None
            order_item.save()


class ReceiptMixin(GetObjectMixin):
    def get_receipt_list(self, user):
        payments = Payment.objects.filter(
            user=user, payment_status__in=["completed", "refunded"]
        ).order_by("-paid_at")

        receipt_list = [
            {
                "receipt_number": f"REC-{payment.id}",
                "payment_status": payment.payment_status,
                "amount": payment.amount,
                "paid_at": (
                    payment.paid_at.strftime("%Y-%m-%d %H:%M:%S")
                    if payment.paid_at
                    else None
                ),
                "order_id": payment.order.id,
            }
            for payment in payments
        ]

        return receipt_list

    def get_receipt_detail(self, payment, user):
        order = payment.order
        billing_address = payment.billing_address

        receipt_data = {
            "receipt_number": f"REC-{payment.id}",
            "issue_date": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
            "payment_info": {
                "payment_id": payment.id,
                "amount": payment.amount,
                "payment_status": payment.payment_status,
                "paid_at": (
                    payment.paid_at.strftime("%Y-%m-%d %H:%M:%S")
                    if payment.paid_at
                    else None
                ),
            },
            "order_info": {
                "order_id": order.id,
                "order_status": order.order_status,
                "total_items": order.get_total_items(),
                "total_price": order.get_total_price(),
                "items": [
                    {
                        "name": item.get_item_name(),
                        "quantity": item.quantity,
                        "price": item.get_price(),
                    }
                    for item in order.order_items.all()
                ],
            },
            "customer_info": {"email": user.email},
            "billing_address": None,
        }

        if billing_address:
            receipt_data["billing_address"] = {
                "country": billing_address.country,
                "main_address": billing_address.main_address,
                "detail_address": billing_address.detail_address,
                "postal_code": billing_address.postal_code,
            }

        return receipt_data
