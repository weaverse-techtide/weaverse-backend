from rest_framework import serializers
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    """
    장바구니에 담긴 상품 모델의 시리얼라이저입니다.
    """

    class Meta:
        model = CartItem
        fields = [
            "id",
            "cart",
            "item_type",
            "quantity",
            "created_at",
            "updated_at",
            "curriculum",
            "course",
        ]

    def validate(self, data):
        """
        커리큘럼과 코스 중 하나만 선택되었는지 확인합니다.

        Raises:
            serializers.ValidationError: 커리큘럼과 코스가 모두 선택되지 않았거나, 둘 다 선택된 경우.
        """
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
    장바구니 모델의 시리얼라이저입니다. 상품의 수량 필드를 포함합니다.
    """

    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "items"]
