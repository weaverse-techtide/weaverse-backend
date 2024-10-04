from rest_framework import serializers

from .models import Cart, CartItem, Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """
    주문 상품 모델의 시리얼라이저입니다.
    """

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "curriculum",
            "course",
            "quantity",
            "created_at",
            "updated_at",
            "item_name",
            "price",
        ]
        read_only_fields = [
            "item_name",
            "price",
            "quantity",
        ]

    def validate(self, data):
        # 커리큘럼과 코스 중 하나만 선택되었는지 확인합니다.
        curriculum = data.get("curriculum")
        course = data.get("course")
        if not curriculum and not course:
            raise serializers.ValidationError(
                "커리큘럼 또는 코스 중 하나를 선택해야 합니다."
            )
        if curriculum and course:
            raise serializers.ValidationError(
                "커리큘럼과 코스 중 하나만 선택해야 합니다."
            )
        return data


class OrderSerializer(serializers.ModelSerializer):
    """
    주문 모델의 시리얼라이저입니다. 총 상품 수량과 가격을 계산합니다.
    """

    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "order_items",
            "total_items",
            "total_price",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "total_items",
            "total_price",
        ]


class CartItemSerializer(serializers.ModelSerializer):
    """
    장바구니에 담긴 상품 모델의 시리얼라이저입니다.
    """

    class Meta:
        model = CartItem
        fields = [
            "id",
            "cart",
            "curriculum",
            "course",
            "quantity",
            "created_at",
            "updated_at",
            "item_name",
            "price",
        ]
        read_only_fields = [
            "item_name",
            "price",
            "quantity",
        ]

    def validate(self, data):
        # 커리큘럼과 코스 중 하나만 선택되었는지 확인합니다.
        curriculum = data.get("curriculum")
        course = data.get("course")
        if not curriculum and not course:
            raise serializers.ValidationError(
                "커리큘럼 또는 코스 중 하나를 선택해야 합니다."
            )
        if curriculum and course:
            raise serializers.ValidationError(
                "커리큘럼과 코스 중 하나만 선택해야 합니다."
            )
        return data


class CartSerializer(serializers.ModelSerializer):
    """
    장바구니 모델의 시리얼라이저입니다. 총 상품 수량과 가격을 계산합니다.
    """

    cart_items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = [
            "id",
            "user",
            "cart_items",
            "total_items",
            "total_price",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "total_items",
            "total_price",
        ]
