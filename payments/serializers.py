from rest_framework import serializers

from .models import Cart, CartItem, Order, OrderItem, Payment, UserBillingAddress


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
            "get_item_name",
            "get_price",
            "get_image_url",
        ]
        read_only_fields = [
            "id",
            "cart",
            "quantity",
            "created_at",
            "updated_at",
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
            "get_total_items",
            "get_total_price",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    """
    주문 상품 모델의 시리얼라이저입니다.
    """

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "order",
            "curriculum",
            "course",
            "quantity",
            "created_at",
            "updated_at",
            "expiry_date",
            "get_item_name",
            "get_price",
            "get_image_url",
        ]
        read_only_fields = [
            "id",
            "quantity",
            "created_at",
            "updated_at",
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
            "order_status",
            "created_at",
            "updated_at",
            "get_total_items",
            "get_total_price",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class UserBillingAddressSerializer(serializers.ModelSerializer):
    """
    사용자의 결제 수단 모델의 시리얼라이저입니다.
    """

    class Meta:
        model = UserBillingAddress
        fields = [
            "id",
            "user",
            "country",
            "main_address",
            "detail_address",
            "postal_code",
            "is_default",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class PaymentSerializer(serializers.ModelSerializer):
    """
    결제 모델의 시리얼라이저입니다.
    """

    class Meta:
        model = Payment
        fields = [
            "id",
            "user",
            "order",
            "payment_status",
            "amount",
            "transaction_id",
            "created_at",
            "updated_at",
            "paid_at",
            "cancelled_at",
            "billing_address",
        ]
        read_only_fields = [
            "id",
            "user",
            "order",
            "payment_status",
            "payment_method",
            "amount",
            "transaction_id",
            "created_at",
            "updated_at",
            "paid_at",
            "cancelled_at",
        ]
