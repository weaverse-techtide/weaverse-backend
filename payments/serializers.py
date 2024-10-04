from rest_framework import serializers

from .models import Cart, CartItem, Order, OrderItem


class CartItemSerializer(serializers.ModelSerializer):
    """
    장바구니에 담긴 상품 모델의 시리얼라이저입니다.
    """

    curriculum_name = serializers.SerializerMethodField()
    course_title = serializers.SerializerMethodField()
    curriculum_price = serializers.SerializerMethodField()
    course_price = serializers.SerializerMethodField()

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
            "curriculum_name",
            "course_title",
            "curriculum_price",
            "course_price",
        ]
        read_only_fields = [
            "curriculum_name",
            "course_title",
            "curriculum_price",
            "course_price",
            "quantity",
        ]

    def get_curriculum_name(self, obj):
        return obj.curriculum.name if obj.curriculum else None

    def get_course_title(self, obj):
        return obj.course.title if obj.course else None

    def get_curriculum_price(self, obj):
        return obj.curriculum.price if obj.curriculum else None

    def get_course_price(self, obj):
        return obj.course.price if obj.course else None

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
    total_items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "cart_items",
            "total_items",
            "total_price",
            "created_at",
            "updated_at",
        ]

    def get_total_items(self, obj):
        return obj.cart_items.count()

    def get_total_price(self, obj):
        total = sum(
            [
                item.curriculum.price if item.curriculum else item.course.price
                for item in obj.cart_items.all()
            ]
        )
        return total


class OrderItemSerializer(serializers.ModelSerializer):
    """
    주문 상품 모델의 시리얼라이저입니다.
    """

    curriculum_name = serializers.SerializerMethodField()
    course_title = serializers.SerializerMethodField()
    curriculum_price = serializers.SerializerMethodField()
    course_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "curriculum",
            "course",
            "quantity",
            "created_at",
            "updated_at",
            "curriculum_name",
            "course_title",
            "curriculum_price",
            "course_price",
        ]
        read_only_fields = [
            "curriculum_name",
            "course_title",
            "curriculum_price",
            "course_price",
            "quantity",
        ]

    def get_curriculum_name(self, obj):
        return obj.curriculum.name if obj.curriculum else None

    def get_course_title(self, obj):
        return obj.course.title if obj.course else None

    def get_curriculum_price(self, obj):
        return obj.curriculum.price if obj.curriculum else None

    def get_course_price(self, obj):
        return obj.course.price if obj.course else None

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
    total_items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            "id",
            "user",
            "order_items",
            "total_items",
            "total_price",
            "created_at",
            "updated_at",
        ]

    def get_total_items(self, obj):
        return obj.order_items.count()

    def get_total_price(self, obj):
        total = sum(
            [
                item.curriculum.price if item.curriculum else item.course.price
                for item in obj.order_items.all()
            ]
        )
        return total
