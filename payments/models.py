from django.db import models
from django.conf import settings

from courses.models import Curriculum, Course


class Order(models.Model):
    """
    주문 모델입니다.
    """

    ORDER_STATUS_CHOICES = [
        ("pending", "대기 중"),
        ("completed", "완료됨"),
        ("canceled", "취소됨"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="사용자"
    )
    order_status = models.CharField(
        max_length=10,
        choices=ORDER_STATUS_CHOICES,
        default="pending",
        verbose_name="주문 상태",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    @property
    def total_items(self):
        return sum(item.quantity for item in self.order_items.all())

    @property
    def total_price(self):
        return sum(item.price for item in self.order_items.all())

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "주문"
        verbose_name_plural = "주문들"

    def __str__(self):
        return f"{self.user.nickname}의 주문"


class OrderItem(models.Model):
    """
    주문 상품 모델입니다.
    """

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_items", verbose_name="주문"
    )
    curriculum = models.OneToOneField(
        Curriculum,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="커리큘럼",
    )
    course = models.OneToOneField(
        Course, on_delete=models.CASCADE, null=True, blank=True, verbose_name="코스"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="수량")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    @property
    def item_name(self):
        return (
            self.curriculum.name
            if self.curriculum
            else self.course.title if self.course else "상품"
        )

    @property
    def price(self):
        return (
            self.curriculum.price
            if self.curriculum
            else self.course.price if self.course else 0
        )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "주문 상품"
        verbose_name_plural = "주문 상품들"

    def __str__(self):
        return f"{self.cart.user.nickname}의 주문에 있는 {self.item_name}"


class Cart(models.Model):
    """
    사용자의 장바구니 모델입니다.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="사용자"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    @property
    def total_items(self):
        return sum(item.quantity for item in self.cart_items.all())

    @property
    def total_price(self):
        return sum(item.price for item in self.cart_items.all())

    class Meta:
        verbose_name = "장바구니"

    def __str__(self):
        return f"{self.user.nickname}의 장바구니"


class CartItem(models.Model):
    """
    장바구니에 담긴 상품 모델입니다.
    """

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name="장바구니",
    )
    curriculum = models.OneToOneField(
        Curriculum,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="커리큘럼",
    )
    course = models.OneToOneField(
        Course, on_delete=models.CASCADE, null=True, blank=True, verbose_name="코스"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="수량")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    @property
    def item_name(self):
        return (
            self.curriculum.name
            if self.curriculum
            else self.course.title if self.course else "상품"
        )

    @property
    def price(self):
        return (
            self.curriculum.price
            if self.curriculum
            else self.course.price if self.course else 0
        )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "장바구니 상품"
        verbose_name_plural = "장바구니 상품들"

    def __str__(self):
        return f"{self.cart.user.nickname}의 장바구니에 있는 {self.item_name}"


class Payment(models.Model):
    """
    결제 모델입니다.
    """

    PAYMENT_STATUS_CHOICES = [
        ("pending", "대기 중"),
        ("completed", "완료됨"),
        ("canceled", "취소됨"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("credit_card", "신용카드"),
        ("kakaopay", "카카오페이"),
        ("bank_transfer", "계좌 이체"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="사용자"
    )
    order = models.OneToOneField(Order, on_delete=models.CASCADE, verbose_name="주문")
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending",
        verbose_name="결제 상태",
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default="credit_card",
        verbose_name="결제 방식",
    )
    payment_amount = models.PositiveIntegerField(verbose_name="결제 금액")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        verbose_name = "결제"

    def __str__(self):
        return f"{self.user.nickname}의 결제"


class UserBillingAddress(models.Model):
    """
    사용자의 청구 주소 모델입니다.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="사용자"
    )
    country = models.CharField(max_length=50, verbose_name="국가")
    main_address = models.CharField(
        max_length=255,
        verbose_name="주소",
        help_text="도로명 주소 또는 지번 주소를 입력하세요.",
    )
    detail_address = models.CharField(
        max_length=255,
        verbose_name="상세 주소",
        help_text="아파트 동/호수, 건물 이름과 호수를 입력하세요.(선택 사항)",
    )
    postal_code = models.CharField(max_length=50, verbose_name="우편번호")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        verbose_name = "사용자 청구 주소"

    def __str__(self):
        return f"{self.user.nickname}의 청구 주소"


class UserBillingInfo(models.Model):
    """
    사용자의 청구 정보 모델입니다.
    """

    PAYMENT_METHOD_CHOICES = [
        ("credit_card", "신용카드"),
        ("kakaopay", "카카오페이"),
        ("bank_transfer", "계좌 이체"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="사용자"
    )
    billing_address = models.OneToOneField(
        UserBillingAddress,
        on_delete=models.CASCADE,
        verbose_name="청구 주소",
        related_name="billing_info",
    )
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES, verbose_name="결제 방식"
    )
    stripe_customer_id = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Stripe 고객 ID"
    )
    stripe_payment_method_id = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Stripe 결제 방법 ID"
    )
    kakaopay_tid = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="KakaoPay 거래 ID"
    )
    bank_account_number = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="계좌 번호"
    )
    bank_name = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="은행 이름"
    )
    bank_transfer_status = models.CharField(
        max_length=20,
        choices=[("pending", "대기 중"), ("completed", "완료")],
        default="pending",
        verbose_name="계좌 이체 상태",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        verbose_name = "사용자 청구 정보"
        verbose_name_plural = "사용자 청구 정보들"
        ordering = ["-created_at"]
        db_table = "user_billing_info"

    def __str__(self):
        return f"{self.user.nickname}의 청구 정보"
