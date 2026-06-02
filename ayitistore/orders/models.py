from django.db import models
from django.contrib.auth.models import User
from store.models import Product, ProductVariant
import uuid


PAYMENT_METHOD_CHOICES = [
    ('paypal', 'PayPal'),
    ('moncash', 'MonCash'),
    ('natcash', 'NatCash'),
    ('cash', 'Paiement à la livraison'),
]

ORDER_STATUS_CHOICES = [
    ('pending', 'En attente'),
    ('confirmed', 'Confirmé'),
    ('processing', 'En traitement'),
    ('shipped', 'Expédié'),
    ('delivered', 'Livré'),
    ('cancelled', 'Annulé'),
    ('refunded', 'Remboursé'),
]

PAYMENT_STATUS_CHOICES = [
    ('pending', 'En attente'),
    ('paid', 'Payé'),
    ('failed', 'Échoué'),
    ('refunded', 'Remboursé'),
]


class Order(models.Model):
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    session_key = models.CharField(max_length=40, blank=True)

    # Shipping info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20, blank=True)

    # Payment
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_id = models.CharField(max_length=200, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)

    # Order
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Commande #{self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"AYT{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=200)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=20, blank=True)
    color = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    @property
    def total_price(self):
        return self.product_price * self.quantity


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='cart')
    session_key = models.CharField(max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Panier - {self.user or self.session_key}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.cart_items.all())

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.cart_items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=20, blank=True)
    color = models.CharField(max_length=50, blank=True)

    class Meta:
        unique_together = ('cart', 'product', 'size', 'color')

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

    @property
    def unit_price(self):
        base = self.product.price
        if self.variant:
            base += self.variant.price_adjustment
        return base

    @property
    def total_price(self):
        return self.unit_price * self.quantity


class ShippingTracking(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tracking')
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES)
    description = models.TextField()
    location = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order.order_number} - {self.get_status_display()}"
