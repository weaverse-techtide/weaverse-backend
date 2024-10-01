from django.urls import path
from .views import CartItemView

app_name = "payments"

urlpatterns = [
    path("cart/", CartItemView.as_view(), name="cart"),
    path("cart/item/<int:item_id>/", CartItemView.as_view(), name="cart-item"),
]
