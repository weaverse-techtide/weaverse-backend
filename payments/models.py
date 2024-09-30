from django.db import models
from django.conf import settings

from courses.models import Curriculum, Course


class Cart(models.Model):
    """
    유저의 장바구니 모델입니다.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}의 장바구니"


class CartItem(models.Model):
    """
    장바구니에 담긴 상품 모델입니다.
    """

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    curriculum = models.OneToOneField(
        Curriculum, on_delete=models.CASCADE, null=True, blank=True
    )
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.cart.user.email}의 장바구니에 담긴 {self.curriculum.name}"
