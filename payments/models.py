from django.db import models
from django.utils import timezone
from django.conf import settings

from courses.models import Curriculum, Course


class Cart(models.Model):
    """
    사용자의 장바구니 모델입니다.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="사용자"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    def get_total_items(self):
        return sum(item.quantity for item in self.cart_items.all())

    def get_total_price(self):
        return sum(item.get_price() for item in self.cart_items.all())

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
    curriculum = models.ForeignKey(
        Curriculum,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="커리큘럼",
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, null=True, blank=True, verbose_name="코스"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="수량")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    def get_item_name(self):
        if self.curriculum:
            return self.curriculum.name
        elif self.course:
            return self.course.title
        else:
            return "알 수 없는 상품"

    def get_price(self):
        unit_price = 0
        if self.curriculum:
            unit_price = self.curriculum.price
        elif self.course:
            unit_price = self.course.price
        return unit_price * self.quantity

    def get_image_url(self):
        if self.curriculum and hasattr(self.curriculum, "images"):
            return self.curriculum.images.url
        elif self.course and hasattr(self.course, "images"):
            return self.course.images.url
        return None

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "장바구니 상품"
        verbose_name_plural = "장바구니 상품들"

    def __str__(self):
        try:
            user_nickname = self.cart.user.nickname
            item_name = (
                self.curriculum.name
                if self.curriculum
                else self.course.title if self.course else "알 수 없는 상품"
            )
            return f"{user_nickname}의 장바구니에 있는 {item_name}"
        except Exception as e:
            return f"장바구니 상품 (ID: {self.id})"


class Order(models.Model):
    """
    주문 모델입니다.
    """

    ORDER_STATUS_CHOICES = [
        ("pending", "대기 중"),
        ("completed", "완료됨"),
        ("failed", "실패함"),
        ("cancelled", "취소됨"),
        ("refunded", "환불됨"),
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

    def get_total_items(self):
        return sum(item.quantity for item in self.order_items.all())

    def get_total_price(self):
        return sum(item.get_price() for item in self.order_items.all())

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
    curriculum = models.ForeignKey(
        "courses.Curriculum",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="커리큘럼",
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="코스",
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="수량")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")
    expiry_date = models.DateTimeField(null=True, blank=True, verbose_name="만료일")

    def get_item_name(self):
        if self.curriculum:
            return self.curriculum.name
        elif self.course:
            return self.course.title
        else:
            return "알 수 없는 상품"

    def get_price(self):
        unit_price = 0
        if self.curriculum:
            unit_price = self.curriculum.price
        elif self.course:
            unit_price = self.course.price
        return unit_price * self.quantity

    def get_image_url(self):
        if self.curriculum and hasattr(self.curriculum, "images"):
            return self.curriculum.images.url
        elif self.course and hasattr(self.course, "images"):
            return self.course.images.url
        return None

    def save(self, *args, **kwargs):
        if self.order.order_status == "completed" and (
            not self.expiry_date or self.expiry_date < timezone.now()
        ):
            self.expiry_date = timezone.now() + timezone.timedelta(days=730)  # 2년
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "주문 상품"
        verbose_name_plural = "주문 상품들"

    def __str__(self):
        try:
            user_nickname = self.order.user.nickname
            item_name = (
                self.curriculum.name
                if self.curriculum
                else self.course.title if self.course else "알 수 없는 상품"
            )
            return f"{user_nickname}의 주문에 있는 {item_name}"
        except Exception as e:
            return f"주문 상품 (ID: {self.id})"


class UserBillingAddress(models.Model):
    """
    사용자 청구 주소 모델입니다.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="사용자"
    )
    country = models.CharField(max_length=50, verbose_name="국가")
    main_address = models.CharField(max_length=255, verbose_name="주소")
    detail_address = models.CharField(
        max_length=255, verbose_name="상세 주소", blank=True
    )
    postal_code = models.CharField(max_length=20, verbose_name="우편번호")
    is_default = models.BooleanField(default=False, verbose_name="기본 주소")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "사용자 청구 주소"
        verbose_name_plural = "사용자 청구 주소들"

    def __str__(self):
        return f"{self.user.nickname}의 청구 주소"

    def save(self, *args, **kwargs):
        # 기본 주소가 설정되어 있으면, 사용자의 다른 기본 주소를 해제합니다.
        if self.is_default:
            UserBillingAddress.objects.filter(user=self.user, is_default=True).update(
                is_default=False
            )
        super().save(*args, **kwargs)


class Payment(models.Model):
    """
    결제 모델입니다.
    """

    PAYMENT_STATUS_CHOICES = [
        ("pending", "대기 중"),
        ("completed", "완료됨"),
        ("failed", "실패함"),
        ("cancelled", "취소됨"),
        ("refunded", "환불됨"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="사용자"
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="주문")
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending",
        verbose_name="결제 상태",
    )
    amount = models.PositiveIntegerField(verbose_name="결제 금액")
    transaction_id = models.CharField(
        max_length=255, verbose_name="거래 ID", blank=True, null=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True, blank=True, null=True, verbose_name="생성일"
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="결제 일시")
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name="취소 일시")
    fail_reason = models.TextField(verbose_name="실패 사유", blank=True, null=True)
    billing_address = models.ForeignKey(
        UserBillingAddress,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="청구 주소",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "결제"
        verbose_name_plural = "결제들"

    def __str__(self):
        return f"{self.user.nickname}의 결제 ({self.get_payment_status_display()})"

    def save(self, *args, **kwargs):
        if not self.billing_address:
            self.billing_address = UserBillingAddress.objects.filter(
                user=self.user, is_default=True
            ).first()
        super().save(*args, **kwargs)
