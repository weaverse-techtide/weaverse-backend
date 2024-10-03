from django.urls import path

from .views import CartItemView

urlpatterns = [
    path("cart/items/", CartItemView.as_view(), name="cart-items"),
    path("cart/items/<int:item_id>/", CartItemView.as_view(), name="cart-item-detail"),
]
