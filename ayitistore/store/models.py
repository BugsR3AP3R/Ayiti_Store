from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify


GENRE_CHOICES = [
    ('homme', 'Homme'),
    ('femme', 'Femme'),
    ('garcon', 'Garçons'),
    ('fille', 'Filles'),
    ('unisex', 'Unisexe'),
]

TYPE_CHOICES = [
    ('vetement', 'Vêtement'),
    ('accessoire', 'Accessoire'),
    ('chaussure', 'Chaussure'),
    ('sac', 'Sac'),
    ('bijou', 'Bijou'),
]


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES)
    type_produit = models.CharField(max_length=20, choices=TYPE_CHOICES, default='vetement')
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Catégories'

    def __str__(self):
        return f"{self.get_genre_display()} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.genre}-{self.name}")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('store:category', kwargs={'slug': self.slug})


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_new = models.BooleanField(default=True)
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES)
    type_produit = models.CharField(max_length=20, choices=TYPE_CHOICES, default='vetement')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('store:product_detail', kwargs={'slug': self.slug})

    @property
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return int((1 - self.price / self.old_price) * 100)
        return 0

    @property
    def main_image(self):
        img = self.images.filter(is_main=True).first()
        return img if img else self.images.first()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_main = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.product.name} - image {self.order}"


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    size = models.CharField(max_length=20, blank=True)
    color = models.CharField(max_length=50, blank=True)
    color_hex = models.CharField(max_length=7, blank=True, default='#000000')
    stock = models.PositiveIntegerField(default=0)
    price_adjustment = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    def __str__(self):
        parts = []
        if self.size:
            parts.append(f"Taille: {self.size}")
        if self.color:
            parts.append(f"Couleur: {self.color}")
        return f"{self.product.name} - {' / '.join(parts)}"


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}/5)"
