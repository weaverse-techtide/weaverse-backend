from rest_framework import serializers

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    """
    상품 모델의 시리얼라이저입니다. 코스 모델의 일부 필드를 포함합니다.
    """

    course_title = serializers.CharField(source="course.title", read_only=True)
    course_category = serializers.CharField(source="course.category", read_only=True)
    course_level = serializers.CharField(source="course.course_level", read_only=True)

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
