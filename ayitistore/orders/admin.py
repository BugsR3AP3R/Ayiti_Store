from django.contrib import admin
from .models import Order, OrderItem, Cart, CartItem, ShippingTracking


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class ShippingTrackingInline(admin.TabularInline):
    model = ShippingTracking
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'total', 'payment_method', 'payment_status', 'status', 'created_at']
    list_filter = ['status', 'payment_status', 'payment_method']
    search_fields = ['order_number', 'first_name', 'last_name', 'email']
    inlines = [OrderItemInline, ShippingTrackingInline]
