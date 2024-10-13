from django.contrib import admin
from .models import Cart, Order, Payment, UserBillingAddress


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "get_total_items", "get_total_price", "created_at")
    search_fields = ("user__email", "user__nickname")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "order_status",
        "get_total_items",
        "get_total_price",
        "created_at",
    )
    list_filter = ("order_status",)
    search_fields = ("user__email", "user__nickname")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "order", "payment_status", "amount", "paid_at")
    list_filter = ("payment_status",)
    search_fields = ("user__email", "user__nickname", "transaction_id")


@admin.register(UserBillingAddress)
class UserBillingAddressAdmin(admin.ModelAdmin):
    list_display = ("user", "country", "main_address", "is_default")
    list_filter = ("country", "is_default")
    search_fields = ("user__email", "user__nickname", "main_address")
