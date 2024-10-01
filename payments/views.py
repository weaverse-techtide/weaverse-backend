from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Cart, CartItem
from .serializers import CartItemSerializer, CartSerializer


@extend_schema_view(
    get=extend_schema(
        summary="장바구니 조회",
        description="사용자의 장바구니를 조회합니다.",
        responses={200: CartSerializer},
    ),
    post=extend_schema(
        summary="장바구니 아이템 추가",
        description="사용자의 장바구니에 특정 상품을 추가합니다.",
        request=CartItemSerializer,
        responses={201: CartItemSerializer},
    ),
    delete=extend_schema(
        summary="장바구니 아이템 삭제",
        description="사용자의 장바구니에서 특정 상품을 삭제합니다.",
        responses={204: None},
    ),
)
class CartItemView(generics.GenericAPIView):
    """
    사용자의 장바구니를 관리하는 뷰입니다.

    GET:
        사용자의 장바구니를 조회하거나 특정 상품을 조회합니다.
        - item_id가 제공되면 해당 상품을 조회합니다.
        - item_id가 제공되지 않으면 전체 장바구니를 조회합니다.

    POST:
        사용자의 장바구니에 새로운 상품을 추가합니다.

    DELETE:
        사용자의 장바구니에서 특정 상품을 삭제합니다.
    """

    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def _get_cart(self, user):
        """
        사용자별 장바구니를 조회합니다. 없으면 새로 생성합니다.
        """
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    def _get_cart_item(self, cart, item_id):
        """
        사용자별 장바구니에 있는 특정 상품을 조회합니다.
        """
        try:
            return CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response(
                {"detail": "장바구니에 상품이 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def get(self, request, item_id=None):
        """
        사용자의 장바구니를 조회합니다. 특정 상품을 조회할 수도 있습니다.
        """
        cart = self._get_cart(request.user)

        if item_id:
            cart_item = self._get_cart_item(cart, item_id)
            if isinstance(cart_item, Response):
                return cart_item
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data)
        else:
            serializer = CartSerializer(cart)
            total_items = CartItem.objects.filter(cart=cart).count()
            return Response({"cart": serializer.data, "total_items": total_items})

    def post(self, request):
        """
        사용자의 장바구니에 상품을 추가합니다.
        """
        cart = self._get_cart(request.user)
        serializer = CartItemSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(cart=cart)
            return Response(
                {
                    "message": "상품이 장바구니에 추가되었습니다.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "message": "상품을 추가하는 데 실패했습니다.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, item_id):
        """
        사용자의 장바구니에서 특정 상품을 삭제합니다.
        """
        cart = self._get_cart(request.user)
        cart_item = self._get_cart_item(cart, item_id)
        if isinstance(cart_item, Response):
            return cart_item
        cart_item.delete()
        return Response(
            {"message": "상품이 장바구니에서 삭제되었습니다."},
            status=status.HTTP_204_NO_CONTENT,
        )
