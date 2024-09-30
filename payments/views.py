from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from courses.models import Curriculum, Course

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


class CartItemView(APIView):

    def get_cart(self, user):
        """
        사용자별 장바구니를 조회합니다. 없으면 새로 생성합니다.
        """
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    def get_cart_item(self, cart, item_id):
        """
        사용자별 장바구니에 있는 특정 상품을 조회합니다.
        """
        try:
            return CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response(
                {"detail": "카트에 상품이 없습니다."}, status=status.HTTP_404_NOT_FOUND
            )

    def get(self, request, item_id=None):
        """
        장바구니에 있는 상품들을 조회하며, item_id가 주어지면 개별 상품을 조회합니다.
        """
        cart = self.get_cart(request.user)

        if item_id is None:
            serializer = CartSerializer(cart)
        else:
            cart_item = self.get_cart_item(cart, item_id)
            if cart_item is None:
                return Response(
                    {"detail": "장바구니에 상품이 없습니다."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            serializer = CartItemSerializer(cart_item)

        return Response(serializer.data)

    def post(self, request):
        """
        장바구니에 새 상품을 추가합니다.
        """
        cart = self.get_cart(request.user)
        curriculum_id = request.data.get("curriculum_id")
        course_id = request.data.get("course_id")
        quantity = int(request.data.get("quantity", 1))

        if quantity < 0:
            return Response(
                {"detail": "수량은 0 이상이어야 합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            curriculum = Curriculum.objects.get(id=curriculum_id)
        except Curriculum.DoesNotExist:
            return Response(
                {"detail": "해당되는 커리큘럼이 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response(
                {"detail": "해당되는 코스가 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        cart_item, created = CartItem.objects.update_or_create(
            cart=cart,
            course=course,
            curriculum=curriculum,
            defaults={"quantity": quantity},
        )

        serializer = CartItemSerializer(cart_item)
        response_data = serializer.data
        if created:
            response_data["message"] = "장바구니에 새로운 상품이 추가되었습니다."
        else:
            response_data["message"] = "장바구니의 상품이 업데이트되었습니다."

        return Response(
            response_data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def delete(self, request, item_id):
        """
        장바구니에 있는 상품을 삭제합니다.
        """
        cart = self.get_cart(request.user)
        cart_item = self.get_cart_item(cart, item_id)

        if cart_item is None:
            return Response(
                {"detail": "해당되는 상품이 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        cart_item.delete()
        return Response(
            {"message": "장바구니에서 상품이 삭제되었습니다."},
            status=status.HTTP_204_NO_CONTENT,
        )
