from django.urls import path
from .views import (
    CartItemListCreateView,
    CartItemDestroyView,
    OrderItemListCreateView,
    OrderItemDestroyView,
    CartToOrderConversionView,
)

app_name = "payments"

urlpatterns = [
    path("cart/", CartItemListCreateView.as_view(), name="cart"),
    path("cart/item/<int:pk>/", CartItemDestroyView.as_view(), name="cart-item"),
    path("order/", OrderItemListCreateView.as_view(), name="order"),
    path(
        "order/item/<int:pk>/",
        OrderItemDestroyView.as_view(),
        name="order-item",
    ),
    path("cart-to-order/", CartToOrderConversionView.as_view(), name="cart-to-order"),
]
