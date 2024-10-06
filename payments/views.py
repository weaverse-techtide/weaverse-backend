from django.db import transaction
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Cart, CartItem, Order, OrderItem
from .serializers import (
    CartItemSerializer,
    CartSerializer,
    OrderItemSerializer,
    OrderSerializer,
)


class CartItemListCreateView(generics.GenericAPIView):
    """
    사용자의 장바구니를 조회하고, 상품을 추가합니다.
    - [GET]: 사용자의 장바구니를 조회합니다.
    - [POST]: 사용자의 장바구니에 상품을 추가합니다.
    """

    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(cart__user=self.request.user)

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 상품이 장바구니와 주문에 있는지 확인합니다. 있을 시 예외처리합니다.
        with transaction.atomic():
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

            existing_order_item = OrderItem.objects.filter(
                order__user=request.user,
                curriculum=serializer.validated_data.get("curriculum"),
                course=serializer.validated_data.get("course"),
            ).first()

            if existing_order_item:
                return Response(
                    {"detail": "이 상품은 이미 주문 목록에 있습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer.save(cart=cart)

        return Response(
            {"detail": "상품이 장바구니에 추가되었습니다.", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )


class CartItemDestroyView(generics.GenericAPIView):
    """
    [DELETE]: 사용자의 장바구니에서 특정 상품을 삭제합니다.
    """

    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(cart__user=self.request.user)

    def delete(self, request, pk):
        cart_item = self.get_queryset().filter(pk=pk).first()
        if not cart_item:
            return Response(
                {"detail": "상품이 없습니다."}, status=status.HTTP_404_NOT_FOUND
            )
        cart_item.delete()
        return Response(
            {"detail": "상품이 장바구니에서 삭제되었습니다."},
            status=status.HTTP_204_NO_CONTENT,
        )


class OrderItemListCreateView(generics.GenericAPIView):
    """
    사용자의 주문을 조회하고, 상품을 추가합니다.
    - [GET]: 사용자의 주문 항목을 조회합니다.
    - [POST]: 사용자의 주문에 상품을 추가합니다.
    """

    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(order__user=self.request.user)

    def get(self, request):
        order, _ = Order.objects.get_or_create(user=request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def post(self, request):
        order, _ = Order.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 상품이 장바구니와 주문에 있는지 확인합니다. 있을 시 예외처리합니다.
        with transaction.atomic():
            existing_item = OrderItem.objects.filter(
                order=order,
                curriculum=serializer.validated_data.get("curriculum"),
                course=serializer.validated_data.get("course"),
            ).first()

            if existing_item:
                return Response(
                    {"detail": "이 상품은 이미 주문 목록에 있습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            existing_cart_item = CartItem.objects.filter(
                cart__user=request.user,
                curriculum=serializer.validated_data.get("curriculum"),
                course=serializer.validated_data.get("course"),
            ).first()

            if existing_cart_item:
                return Response(
                    {"detail": "이 상품은 이미 장바구니에 있습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer.save(order=order)

        return Response(
            {"detail": "상품이 주문에 추가되었습니다.", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )


class OrderItemDestroyView(generics.GenericAPIView):
    """
    [DELETE]: 사용자의 주문에서 특정 상품을 삭제합니다.
    """

    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(order__user=self.request.user)

    def delete(self, request, pk):
        order_item = self.get_queryset().filter(pk=pk).first()
        if not order_item:
            return Response(
                {"detail": "상품이 없습니다."}, status=status.HTTP_404_NOT_FOUND
            )
        order_item.delete()
        return Response(
            {"detail": "상품이 주문에서 삭제되었습니다."},
            status=status.HTTP_204_NO_CONTENT,
        )


class CartToOrderConversionView(generics.GenericAPIView):
    """
    [POST]: 사용자의 장바구니에 있는 모든 상품을 주문으로 전환합니다.
    """

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        cart, _ = Cart.objects.get_or_create(user=user)
        order, _ = Order.objects.get_or_create(user=user)
        if not cart or not cart.cart_items.exists():
            return Response(
                {"detail": "장바구니가 비어있습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 장바구니에 있는 모든 상품을 주문으로 전환합니다. 이미 주문에 있는 상품은 건너뜁니다.
        with transaction.atomic():
            for cart_item in cart.cart_items.all():
                existing_order_item = OrderItem.objects.filter(
                    order=order,
                    curriculum=cart_item.curriculum,
                    course=cart_item.course,
                ).first()

                if existing_order_item:
                    continue

                OrderItem.objects.create(
                    order=order,
                    curriculum=cart_item.curriculum,
                    course=cart_item.course,
                    quantity=cart_item.quantity,
                )

            cart.cart_items.all().delete()

        serializer = OrderSerializer(order)
        return Response(
            {
                "detail": "장바구니의 모든 상품이 주문으로 전환되었습니다.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
