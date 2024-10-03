from rest_framework import serializers

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    """
    상품 모델의 시리얼라이저입니다. 커리큘럼 이름을 포함합니다.
    """

    curriculum_name = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = "__all__"


class CartSerializer(serializers.ModelSerializer):
    """
    장바구니 모델의 시리얼라이저입니다. 상품의 수량 필드를 포함합니다.
    """

    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = "__all__"

    def get_total_items(self, obj):
        """
        장바구니에 담긴 아이템의 총 개수를 반환합니다.
        """
        return sum(item.quantity for item in obj.items.all())
