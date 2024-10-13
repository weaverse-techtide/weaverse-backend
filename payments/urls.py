from django.urls import path
from .views import (
    CartView,
    OrderView,
    UserBillingAddressView,
    PaymentView,
    ReceiptView,
)

app_name = "payments"

urlpatterns = [
    # 장바구니 관련 URLs
    path("cart/", CartView.as_view(), name="cart-list-create"),
    path("cart/<int:pk>/", CartView.as_view(), name="cart-item-delete"),
    # 주문 관련 URLs
    path("orders/", OrderView.as_view(), name="order"),
    # 청구 주소 관련 URLs
    path(
        "billing-addresses/",
        UserBillingAddressView.as_view(),
        name="billing-address-list-create",
    ),
    path(
        "billing-addresses/<int:pk>/",
        UserBillingAddressView.as_view(),
        name="billing-address-detail",
    ),
    # 결제 관련 URLs
    path(
        "payments/",
        PaymentView.as_view(),
        name="payment",
    ),
    path(
        "payments/<int:order_id>/cancel/",
        PaymentView.as_view(),
        name="payment-cancel",
    ),
    # 영수증 관련 URLs
    path("receipts/", ReceiptView.as_view(), name="receipt-list"),
    path(
        "receipts/<int:payment_id>/",
        ReceiptView.as_view(),
        name="receipt-detail",
    ),
]
