from django.core.exceptions import ValidationError
from django.db import transaction
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .mixins import (
    CartMixin,
    OrderMixin,
    PaymentMixin,
    ReceiptMixin,
    UserBillingAddressMixin,
)
from .models import CartItem, Order, Payment, UserBillingAddress
from .permissions import IsOwnerPermission
from .serializers import (
    CartItemSerializer,
    CartSerializer,
    OrderItemSerializer,
    OrderSerializer,
    PaymentSerializer,
    UserBillingAddressSerializer,
)


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
class CartView(CartMixin, generics.GenericAPIView):
    """
    장바구니 관련 기능을 처리합니다.

    [GET /cart/]: 사용자의 장바구니를 조회합니다.
    [GET /cart/{cart_item_id}/]: 사용자의 장바구니에서 특정 상품을 조회합니다.
    [POST /cart/]: 장바구니에 상품을 추가합니다.
    [DELETE /cart/{cart_item_id}/]: 장바구니에서 특정 상품을 삭제합니다.
    """

    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user).select_related(
            "cart", "cart__user"
        )

    def get(self, request, pk=None):
        if pk:
            cart_item = self.get_cart_item(self.get_cart(request.user), pk=pk)
            serializer = self.get_serializer(cart_item)
            return Response(serializer.data)
        else:
            cart = self.get_cart(request.user)
            serializer = CartSerializer(cart)
            return Response(serializer.data)

    def post(self, request):
        cart = self.get_cart(request.user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.add_to_cart(cart, serializer)

    def delete(self, request, pk):
        cart_item = self.get_cart_item(self.get_cart(request.user), pk=pk)
        return self.remove_from_cart(cart_item)


@extend_schema_view(
    get=extend_schema(
        summary="사용자의 진행 중인 주문을 조회하는 API",
        description="사용자의 현재 진행 중인 (order_status=pending) 주문을 조회합니다.",
        responses={200: OrderSerializer},
    ),
    post=extend_schema(
        summary="새로운 주문을 생성하는 API",
        description="장바구니를 통해 주문을 생성하거나 직접 주문을 생성할 수 있습니다. 기존의 진행 중인 주문은 취소 처리됩니다.",
        responses={201: OrderSerializer},
    ),
)
class OrderView(OrderMixin, CartMixin, generics.GenericAPIView):
    """
    주문 관련 기능을 처리합니다.

    [GET /orders/]: 사용자의 현재 진행 중인 (pending 상태의) 주문을 조회합니다.
    [POST /orders/]: 새로운 주문을 생성합니다.
        - from_cart=False: 직접 주문을 생성합니다.
        - from_cart=True: 장바구니를 통해 주문을 생성합니다.
        주의: 새 주문 생성 시 기존의 진행 중인 주문은 자동으로 취소됩니다.
    """

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, order_status="pending")

    def get(self, request):
        pending_order = self.get_queryset().first()
        if pending_order:
            serializer = self.get_serializer(pending_order)
            return Response(serializer.data)
        else:
            return Response(
                {"detail": "현재 진행 중인 주문이 없습니다.", "data": None},
                status=status.HTTP_200_OK,
            )

    @transaction.atomic
    def post(self, request):
        try:
            # 기존의 pending 상태 주문을 cancelled로 변경
            Order.objects.filter(user=request.user, order_status="pending").update(
                order_status="cancelled"
            )

            if request.data.get("from_cart", False):
                cart = self.get_cart(request.user)
                if not cart.cart_items.exists():
                    raise ValidationError("장바구니가 비어 있습니다.")
                order_data = self.create_order_from_cart(request.user, cart)
            else:
                if "order_items" not in request.data or not request.data["order_items"]:
                    raise ValidationError("주문 항목이 없습니다.")
                order_data = self.create_new_order(request.user, request.data)

            order_data["user"] = request.user.id
            serializer = self.get_serializer(data=order_data)
            serializer.is_valid(raise_exception=True)
            order = serializer.save()

            for item_data in order_data["order_items"]:
                item_data["order"] = order.id
                order_item_serializer = OrderItemSerializer(data=item_data)
                order_item_serializer.is_valid(raise_exception=True)
                order_item_serializer.save()

            if request.data.get("from_cart", False):
                cart = self.get_cart(request.user)
                cart.cart_items.all().delete()

            return Response(
                {
                    "detail": "주문이 성공적으로 생성되었습니다.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
class UserBillingAddressView(UserBillingAddressMixin, generics.GenericAPIView):
    """
    청구 주소 관련 기능을 처리합니다.

    [GET /billing-addresses/]: 사용자의 모든 청구 주소 목록을 조회합니다.
    [GET /billing-addresses/{billing_address_id}/]: 사용자의 특정 청구 주소를 조회합니다.
    [POST /billing-addresses/]: 새로운 청구 주소를 생성합니다.
    [PUT /billing-addresses/{billing_address_id}/]: 특정 청구 주소를 수정합니다.
    [DELETE /billing-addresses/{billing_address_id}/]: 특정 청구 주소를 삭제합니다.
    """

    serializer_class = UserBillingAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserBillingAddress.objects.filter(user=self.request.user)

    def get(self, request, pk=None):
        if pk:
            instance = self.get_billing_address(request.user, pk=pk)
            serializer = self.get_serializer(instance)
        else:
            queryset = UserBillingAddress.objects.filter(user=request.user)
            serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.create_billing_address(request.user, serializer)

    def put(self, request, pk):
        instance = self.get_billing_address(request.user, pk=pk)
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.update_billing_address(instance, serializer)

    def delete(self, request, pk):
        instance = self.get_billing_address(request.user, pk=pk)
        return self.delete_billing_address(instance)


@extend_schema_view(
    post=extend_schema(
        summary="결제를 생성하고 카카오페이 결제를 요청하는 API",
        description="현재 진행 중인 (pending 상태의) 주문에 대한 결제를 생성하고 카카오페이 결제를 요청합니다.",
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
class PaymentView(PaymentMixin, OrderMixin, generics.GenericAPIView):
    """
    결제 관련 기능을 처리합니다.

    [POST /payments/]: 현재 진행 중인 주문에 대한 결제를 생성하고 카카오페이 결제를 요청합니다.
    [GET /payments/]: 카카오페이 결제 결과를 처리합니다.
    [DELETE /payments/<order_id>/cancel/]: 결제를 취소하고 환불을 처리합니다.
    """

    serializer_class = PaymentSerializer
    permission_classes = [IsOwnerPermission]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    @transaction.atomic
    def post(self, request):
        order = (
            self.get_queryset()
            .filter(order_status="pending")
            .select_for_update()
            .first()
        )
        if not order:
            return Response(
                {"detail": "진행 중인 주문이 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            payment, kakao_response = self.create_payment(order, request.user)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
    def get(self, request):
        order = (
            self.get_queryset()
            .filter(order_status="pending")
            .select_for_update()
            .first()
        )
        if not order:
            return Response(
                {"detail": "진행 중인 주문이 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        payment = (
            Payment.objects.filter(order=order, payment_status="pending")
            .order_by("-created_at")
            .first()
        )
        if not payment:
            return Response(
                {"detail": "해당 주문에 대한 대기 중인 결제를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        result = request.GET.get("result")
        pg_token = request.GET.get("pg_token")

        if result == "success":
            try:
                self.process_payment(order, payment, pg_token)
                serializer = self.get_serializer(payment)
                return Response(
                    {
                        "detail": "결제가 성공적으로 완료되었습니다.",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            except ValidationError as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        elif result == "cancel":
            self.cancel_payment(order, payment)
            serializer = self.get_serializer(payment)
            return Response(
                {"detail": "결제 과정이 취소되었습니다.", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        elif result == "fail":
            self.fail_payment(payment)
            serializer = self.get_serializer(payment)
            return Response(
                {
                    "detail": "결제 처리 중 오류가 발생했습니다. 나중에 다시 시도해 주세요.",
                    "data": serializer.data,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            return Response(
                {"detail": "올바르지 않은 결제 결과입니다. 다시 시도해 주세요."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @transaction.atomic
    def delete(self, request, order_id):
        try:
            order = (
                self.get_queryset().filter(order_status="completed").get(id=order_id)
            )
        except Order.DoesNotExist:
            return Response(
                {"detail": "결제된 주문을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        payment = self.get_payment(
            request.user, order=order, payment_status="completed"
        )

        try:
            self.refund_payment(order, payment)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(payment)
        return Response(
            {"detail": "결제가 성공적으로 환불되었습니다.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )


@extend_schema_view(
    get=extend_schema(
        summary="영수증 목록 조회 또는 상세 조회 API",
        description="사용자가 결제 완료/환불 한 모든 영수증 목록을 조회하거나, 특정 결제에 대한 상세 영수증 정보를 조회합니다.",
        responses={200: PaymentSerializer(many=True)},
    ),
)
class ReceiptView(ReceiptMixin, PaymentMixin, generics.GenericAPIView):
    """
    영수증 관련 기능을 처리합니다.

    [GET /receipts/]: 사용자의 모든 영수증 목록을 조회합니다.
    [GET /receipts/{payment_id}/]: 특정 결제에 대한 상세 영수증 정보를 조회합니다.
    """

    serializer_class = PaymentSerializer
    permission_classes = [IsOwnerPermission]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get(self, request, payment_id=None):
        if payment_id is None:
            receipt_list = self.get_receipt_list(request.user)
            return Response(receipt_list)
        else:
            payment = self.get_payment(request.user, id=payment_id)
            receipt_detail = self.get_receipt_detail(payment, request.user)
            receipt_detail["id"] = payment.id
            return Response(receipt_detail)
