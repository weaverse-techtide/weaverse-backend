from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Cart, CartItem, Order, Payment, UserBillingAddress
from .serializers import (
    CartItemSerializer,
    CartSerializer,
    OrderItemSerializer,
    OrderSerializer,
    UserBillingAddressSerializer,
    PaymentSerializer,
)
from .services import KakaoPayService


@extend_schema_view(
    get=extend_schema(
        summary="사용자의 장바구니를 조회하는 API",
        description="사용자의 장바구니를 조회하거나 특정 상품을 조회합니다.",
        responses={200: CartSerializer},
    ),
    post=extend_schema(
        summary="장바구니에 상품을 추가하는 API",
        description="장바구니에 새로운 상품을 추가합니다.",
        responses={201: CartItemSerializer},
    ),
    delete=extend_schema(
        summary="장바구니에서 상품을 삭제하는 API",
        description="장바구니에서 특정 상품을 삭제합니다.",
        responses={204: None},
    ),
)
class CartView(generics.GenericAPIView):
    """
    장바구니 관련 기능을 처리합니다.

    [GET /cart/]: 사용자의 장바구니를 조회합니다.
    [GET /cart/{pk}/]: 장바구니에서 특정 상품을 조회합니다.
    [POST /cart/]: 사용자의 장바구니에 상품을 추가합니다.
    [DELETE /cart/{pk}/]: 사용자의 장바구니에서 상품을 삭제합니다.
    """

    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def get(self, request, pk=None):
        if pk:
            cart_item = get_object_or_404(self.get_queryset(), pk=pk)
            serializer = self.get_serializer(cart_item)
            return Response(serializer.data)
        else:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            if not cart.cart_items.exists():
                return Response(
                    {"detail": "장바구니가 비어있습니다."},
                    status=status.HTTP_200_OK,
                )
            serializer = CartSerializer(cart)
            return Response(serializer.data)

    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

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

        serializer.save(cart=cart)

        return Response(
            {"detail": "상품이 장바구니에 추가되었습니다.", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, pk):
        cart_item = get_object_or_404(self.get_queryset(), pk=pk)
        cart_item.delete()
        return Response(
            {"detail": "상품이 장바구니에서 삭제되었습니다."},
            status=status.HTTP_204_NO_CONTENT,
        )


@extend_schema_view(
    get=extend_schema(
        summary="사용자의 주문 목록을 조회하는 API",
        description="사용자의 모든 주문 목록을 조회하거나 특정 주문을 조회합니다.",
        responses={200: OrderSerializer(many=True)},
    ),
    post=extend_schema(
        summary="새로운 주문을 생성하는 API",
        description="주문을 바로 생성합니다. 혹은 장바구니를 통해 주문을 생성합니다.",
        responses={201: OrderSerializer},
    ),
)
class OrderView(generics.GenericAPIView):
    """
    주문 관련 기능을 처리합니다.

    [GET /orders/]: 사용자의 모든 주문을 조회합니다.
    [GET /orders/{pk}/]: 특정 주문의 상세 정보를 조회합니다.
    [POST /orders/]: 새로운 주문을 생성합니다.
        - from_cart=True: 장바구니를 통해 주문을 생성합니다.
        - from_cart=False: 직접 주문 항목을 지정하여 주문을 생성합니다.
    """

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get(self, request, pk=None):
        if pk:
            instance = get_object_or_404(self.get_queryset(), pk=pk)
            serializer = self.get_serializer(instance)
        else:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.data.get("from_cart", False):
            return self._create_order_from_cart(request)

        return self._create_new_order(request)

    def _create_order_from_cart(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        if not cart.cart_items.exists():
            return Response(
                {"detail": "장바구니가 비어있습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if cart.total_price() > 50000:
            return Response(
                {"detail": "상품의 총 가격이 50,000원을 초과할 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order_data = {
            "user": request.user.id,
            "order_status": "pending",
            "order_items": [
                {
                    "curriculum": item.curriculum.id if item.curriculum else None,
                    "course": item.course.id if item.course else None,
                    "quantity": item.quantity,
                    "price": item.price(),
                }
                for item in cart.cart_items.all()
            ],
        }

        return self._save_order(order_data, from_cart=True)

    def _create_new_order(self, request):
        order_data = request.data.copy()
        if "order_items" not in order_data or not order_data["order_items"]:
            return Response(
                {"detail": "주문 항목이 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order_data["user"] = request.user.id
        order_data["order_status"] = "pending"
        return self._save_order(order_data, from_cart=False)

    def _save_order(self, order_data, from_cart=False):
        order_serializer = self.get_serializer(data=order_data)
        order_serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            order = order_serializer.save()

            for item_data in order_data["order_items"]:
                item_data["order"] = order.id
                order_item_serializer = OrderItemSerializer(data=item_data)
                order_item_serializer.is_valid(raise_exception=True)
                order_item_serializer.save()

            if from_cart:
                # 장바구니를 통한 주문 생성 시에만 장바구니를 비웁니다.
                cart = Cart.objects.get(user=order.user)
                cart.cart_items.all().delete()

        order_serializer = self.get_serializer(order)
        return Response(
            {
                "detail": "주문이 성공적으로 생성되었습니다.",
                "data": order_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema_view(
    get=extend_schema(
        summary="사용자의 청구 주소 목록 또는 특정 청구 주소를 조회하는 API",
        description="사용자의 모든 청구 주소 목록을 조회하거나, 특정 청구 주소를 조회합니다.",
        responses={200: UserBillingAddressSerializer(many=True)},
    ),
    post=extend_schema(
        summary="새로운 청구 주소를 생성하는 API",
        description="새로운 청구 주소를 생성합니다. 바로 기본 청구 주소로 설정됩니다.",
        responses={201: UserBillingAddressSerializer},
    ),
    put=extend_schema(
        summary="특정 청구 주소를 수정하는 API",
        description="청구 주소 ID를 기반으로 특정 청구 주소를 수정합니다.",
        responses={200: UserBillingAddressSerializer},
    ),
    delete=extend_schema(
        summary="특정 청구 주소를 삭제하는 API",
        description="청구 주소 ID를 기반으로 특정 청구 주소를 삭제합니다.",
        responses={204: None},
    ),
)
class UserBillingAddressView(generics.GenericAPIView):
    """
    청구 주소 관련 기능을 처리합니다.

    [GET /billing-addresses/]: 사용자의 모든 청구 주소를 조회합니다.
    [GET /billing-addresses/{pk}/]: 특정 청구 주소의 상세 정보를 조회합니다.
    [POST /billing-addresses/]: 새로운 청구 주소를 생성합니다. 바로 기본 청구 주소로 설정됩니다.
    [PUT /billing-addresses/{pk}/]: 특정 청구 주소를 업데이트합니다.
    [DELETE /billing-addresses/{pk}/]: 특정 청구 주소를 삭제합니다.
    """

    serializer_class = UserBillingAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserBillingAddress.objects.filter(user=self.request.user)

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs.get("pk"))
        return obj

    def get(self, request, pk=None):
        if pk:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
        else:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(user=request.user, is_default=True)

        UserBillingAddress.objects.filter(user=request.user, is_default=True).exclude(
            pk=instance.pk
        ).update(is_default=False)

        return Response(
            {"detail": "청구 주소가 생성되었습니다."}, status=status.HTTP_201_CREATED
        )

    def put(self, request, pk):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "청구 주소가 수정되었습니다.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk):
        instance = self.get_object()
        instance.delete()
        return Response(
            {"detail": "청구 주소가 삭제되었습니다."},
            status=status.HTTP_204_NO_CONTENT,
        )


@extend_schema_view(
    post=extend_schema(
        summary="결제를 생성하고 카카오페이 결제를 요청하는 API",
        description="특정 주문에 대한 결제를 생성하고 카카오페이 결제를 요청합니다.",
        responses={201: PaymentSerializer},
    ),
    get=extend_schema(
        summary="카카오페이 결제 처리 API",
        description="카카오페이 결제 결과를 처리합니다.",
        responses={200: PaymentSerializer},
    ),
    delete=extend_schema(
        summary="결제 취소 및 환불 API",
        description="결제를 취소하고 환불을 처리합니다.",
        responses={200: PaymentSerializer},
    ),
)
class PaymentView(generics.GenericAPIView):
    """
    결제 관련 기능을 처리합니다.

    [POST /payments/{order_id}/]: 특정 주문에 대한 결제를 생성하고 카카오페이 결제를 요청합니다.
    [GET /payments/{order_id}/]: 카카오페이 결제 결과를 처리합니다.
    [DELETE /payments/{order_id}/]: 결제를 취소하고 환불을 처리합니다.
    """

    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kakao_pay_service = KakaoPayService()

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

    def _validate_order(self, order):
        if order.order_status != "pending":
            raise ValidationError("결제 가능한 상태의 주문이 아닙니다.")
        if order.total_price() > 50000:
            raise ValidationError("결제 금액이 50,000원을 초과할 수 없습니다.")
        if hasattr(order, "payment") and order.payment.payment_status == "completed":
            raise ValidationError("이미 결제가 완료된 주문입니다.")

    @transaction.atomic
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        try:
            self._validate_order(order)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            kakao_response = self.kakao_pay_service.request_payment(order)
        except Exception as e:
            return Response(
                {
                    "detail": "결제 요청 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment = Payment.objects.create(
            order=order,
            user=request.user,
            payment_status="pending",
            amount=order.total_price(),
            transaction_id=kakao_response["tid"],
        )

        serializer = self.get_serializer(payment)
        return Response(
            {
                "payment": serializer.data,
                "next_redirect_pc_url": kakao_response["next_redirect_pc_url"],
                "next_redirect_mobile_url": kakao_response["next_redirect_mobile_url"],
                "next_redirect_app_url": kakao_response["next_redirect_app_url"],
            },
            status=status.HTTP_201_CREATED,
        )

    @transaction.atomic
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        payment = get_object_or_404(Payment, order=order)
        result = request.GET.get("result")
        pg_token = request.GET.get("pg_token")

        if result == "success":
            return self._handle_success(request, order, payment, pg_token)
        elif result == "cancel":
            return self._handle_cancel(order, payment)
        elif result == "fail":
            return self._handle_fail(order, payment)
        else:
            return Response(
                {"detail": "올바르지 않은 결제 결과입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def _handle_success(self, request, order, payment, pg_token):
        if not pg_token:
            return Response(
                {"detail": "결제 승인에 필요한 정보가 누락되었습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            self.kakao_pay_service.approve_payment(payment, pg_token)
        except Exception as e:
            order.order_status = "failed"
            order.save()
            payment.payment_status = "failed"
            payment.save()
            return Response(
                {
                    "detail": "결제 승인 중 오류가 발생했습니다. 고객센터로 문의해 주세요."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment.payment_status = "completed"
        payment.paid_at = timezone.now()
        payment.save()
        order.order_status = "completed"
        order.save()

        # OrderItem의 expiry_date 설정
        expiry_date = timezone.now() + timezone.timedelta(days=730)  # 2년
        for order_item in order.order_items.all():
            order_item.expiry_date = expiry_date
            order_item.save()

        serializer = self.get_serializer(payment)
        return Response(
            {"detail": "결제가 성공적으로 완료되었습니다.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def _handle_cancel(self, order, payment):
        payment.payment_status = "cancelled"
        payment.cancelled_at = timezone.now()
        payment.save()
        order.order_status = "cancelled"
        order.save()

        serializer = self.get_serializer(payment)
        return Response(
            {
                "detail": "결제 과정이 사용자에 의해 취소되었습니다.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def _handle_fail(self, order, payment):
        payment.payment_status = "failed"
        payment.save()
        order.order_status = "failed"
        order.save()

        serializer = self.get_serializer(payment)
        return Response(
            {
                "detail": "결제 처리 중 오류가 발생했습니다. 다시 시도해 주세요.",
                "data": serializer.data,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @transaction.atomic
    def delete(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        payment = get_object_or_404(Payment, order=order)

        if payment.payment_status != "completed":
            return Response(
                {"detail": "완료된 결제만 취소할 수 있습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            self.kakao_pay_service.cancel_payment(payment)
        except Exception as e:
            return Response(
                {
                    "detail": "결제 취소 중 오류가 발생했습니다. 고객센터로 문의해 주세요."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment.payment_status = "cancelled"
        payment.cancelled_at = timezone.now()
        payment.save()
        order.order_status = "cancelled"
        order.save()

        # OrderItem의 expiry_date 초기화
        for order_item in order.order_items.all():
            order_item.expiry_date = None
            order_item.save()

        serializer = self.get_serializer(payment)
        return Response(serializer.data)


@extend_schema_view(
    get=extend_schema(
        summary="영수증 목록 조회 또는 상세 조회 API",
        description="사용자의 모든 결제에 대한 영수증 목록을 조회하거나, 특정 결제에 대한 상세 영수증 정보를 조회합니다.",
        responses={200: PaymentSerializer(many=True)},
    ),
)
class ReceiptView(generics.GenericAPIView):
    """
    영수증 조회 관련 기능을 처리합니다.

    [GET /receipts/]: 사용자의 모든 결제에 대한 영수증 목록을 조회합니다.
    [GET /receipts/{payment_id}/]: 특정 결제에 대한 상세 영수증 정보를 조회합니다.
    """

    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

    def get(self, request, payment_id=None):
        if payment_id is None:
            return self.get_receipt_list(request)
        else:
            return self.get_receipt_detail(request, payment_id)

    def get_receipt_list(self, request):
        payments = self.get_queryset().order_by("-paid_at")

        receipt_list = [
            {
                "receipt_number": f"REC-{payment.id}",
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

        return Response(receipt_list)

    def get_receipt_detail(self, request, payment_id):
        payment = get_object_or_404(self.get_queryset(), id=payment_id)
        order = payment.order
        billing_address = payment.billing_address

        receipt_data = {
            "receipt_number": f"REC-{payment.id}",
            "issue_date": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
            "payment_info": {
                "payment_id": payment.id,
                "payment_method": payment.payment_method,
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
                "total_items": order.total_items,
                "total_price": order.total_price,
                "items": [
                    {
                        "name": item.item_name,
                        "quantity": item.quantity,
                        "price": item.price,
                    }
                    for item in order.order_items.all()
                ],
            },
            "customer_info": {
                "email": request.user.email,
            },
        }

        if billing_address:
            receipt_data["billing_address"] = {
                "country": billing_address.country,
                "main_address": billing_address.main_address,
                "detail_address": billing_address.detail_address,
                "postal_code": billing_address.postal_code,
            }

        return Response(receipt_data)
