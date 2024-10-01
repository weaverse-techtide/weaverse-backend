from django.db import models
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

    class Meta:
        verbose_name = "장바구니"

    def __str__(self):
        return f"{self.user.email}의 장바구니"


class CartItem(models.Model):
    """
    장바구니에 담긴 상품 모델입니다.
    """

    ITEM_TYPE_CHOICES = (
        ("curriculum", "커리큘럼"),
        ("course", "코스"),
    )

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
    item_type = models.CharField(
        max_length=10, choices=ITEM_TYPE_CHOICES, verbose_name="상품 유형"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="수량")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "장바구니 상품"
        verbose_name_plural = "장바구니 상품들"

    def __str__(self):
        if self.item_type == "curriculum":
            return f"{self.cart.user.email}의 장바구니에 담긴 {self.curriculum.name}"
        elif self.item_type == "course":
            return f"{self.cart.user.email}의 장바구니에 담긴 {self.course.title}"
        return ValueError("상품 종류가 올바르지 않습니다.")
