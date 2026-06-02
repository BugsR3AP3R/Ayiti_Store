from django.contrib import admin
from .models import Category, Product, ProductImage, ProductVariant, Wishlist, Review


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 2


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'genre', 'type_produit', 'price', 'stock', 'is_available', 'is_featured']
    list_filter = ['genre', 'type_produit', 'is_available', 'is_featured', 'is_new']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariantInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'genre', 'type_produit']
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Wishlist)
admin.site.register(Review)
