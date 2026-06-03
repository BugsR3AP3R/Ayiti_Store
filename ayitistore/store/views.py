from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Avg
from .models import Product, Category, ProductImage, ProductVariant, Wishlist, Review, GENRE_CHOICES, TYPE_CHOICES
from orders.models import Cart, CartItem
import json


def home(request):
    featured = Product.objects.filter(is_featured=True, is_available=True)[:8]
    new_arrivals = Product.objects.filter(is_new=True, is_available=True)[:8]
    categories = Category.objects.all()[:8]
    genres = GENRE_CHOICES
    return render(request, 'store/home.html', {
        'featured': featured,
        'new_arrivals': new_arrivals,
        'categories': categories,
        'genres': genres,
    })


def product_list(request):
    products = Product.objects.filter(is_available=True)
    genre = request.GET.get('genre', '')
    type_produit = request.GET.get('type', '')
    category_slug = request.GET.get('category', '')
    search = request.GET.get('q', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort = request.GET.get('sort', '-created_at')

    if genre:
        products = products.filter(genre=genre)
    if type_produit:
        products = products.filter(type_produit=type_produit)
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if search:
        products = products.filter(Q(name__icontains=search) | Q(description__icontains=search))
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    valid_sorts = ['-created_at', 'price', '-price', 'name', '-name']
    if sort in valid_sorts:
        products = products.order_by(sort)

    categories = Category.objects.all()
    return render(request, 'store/product_list.html', {
        'products': products,
        'categories': categories,
        'current_genre': genre,
        'current_type': type_produit,
        'search': search,
        'sort': sort,
        'genres': GENRE_CHOICES,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_available=True)
    images = product.images.all()
    variants = product.variants.all()
    sizes = variants.values_list('size', flat=True).distinct()
    colors = variants.values_list('color', 'color_hex').distinct()
    reviews = product.reviews.all()
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    related = Product.objects.filter(
        category=product.category, is_available=True
    ).exclude(pk=product.pk)[:4]

    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    if request.method == 'POST' and request.user.is_authenticated:
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        if rating and comment:
            Review.objects.update_or_create(
                product=product, user=request.user,
                defaults={'rating': rating, 'comment': comment}
            )
            messages.success(request, 'Votre avis a été enregistré!')
            return redirect('store:product_detail', slug=slug)

    return render(request, 'store/product_detail.html', {
        'product': product,
        'images': images,
        'variants': variants,
        'sizes': [s for s in sizes if s],
        'colors': [(c[0], c[1]) for c in colors if c[0]],
        'reviews': reviews,
        'avg_rating': avg_rating,
        'related': related,
        'in_wishlist': in_wishlist,
    })


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_available=True)
    return render(request, 'store/category.html', {
        'category': category,
        'products': products,
    })


def genre_products(request, genre):
    genre_dict = dict(GENRE_CHOICES)
    genre_display = genre_dict.get(genre, genre.capitalize())
    selected_type = request.GET.get('type', '')
    sort = request.GET.get('sort', '')
    products = Product.objects.filter(genre=genre, is_available=True)
    if selected_type:
        products = products.filter(type_produit=selected_type)
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    return render(request, 'store/genre.html', {
        'products': products,
        'genre': genre,
        'genre_display': genre_display,
        'type_choices': TYPE_CHOICES,
        'selected_type': selected_type,
    })


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


def cart_view(request):
    cart = get_or_create_cart(request)
    items = cart.cart_items.select_related('product', 'product__category').all()
    shipping_cost = 500 if cart.subtotal < 5000 else 0  # HTG
    total = cart.subtotal + shipping_cost
    return render(request, 'store/cart.html', {
        'cart': cart,
        'items': items,
        'shipping_cost': shipping_cost,
        'total': total,
    })


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_available=True)
    cart = get_or_create_cart(request)
    size = request.POST.get('size', '')
    color = request.POST.get('color', '')
    quantity = int(request.POST.get('quantity', 1))
    variant = None
    if size or color:
        variant = ProductVariant.objects.filter(
            product=product, size=size, color=color
        ).first()

    item, created = CartItem.objects.get_or_create(
        cart=cart, product=product, size=size, color=color,
        defaults={'variant': variant, 'quantity': quantity}
    )
    if not created:
        item.quantity += quantity
        item.save()

    messages.success(request, f'"{product.name}" ajouté au panier!')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_count': cart.total_items})
    return redirect('store:cart')


def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    cart = get_or_create_cart(request)
    if item.cart == cart:
        item.delete()
        messages.success(request, 'Article retiré du panier.')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_count': cart.total_items, 'subtotal': float(cart.subtotal)})
    return redirect('store:cart')


def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    cart = get_or_create_cart(request)
    if item.cart == cart:
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            item.quantity = quantity
            item.save()
        else:
            item.delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'item_total': float(item.total_price) if item.pk else 0,
            'cart_subtotal': float(cart.subtotal),
            'cart_count': cart.total_items
        })
    return redirect('store:cart')


@login_required
def wishlist_view(request):
    wishlist = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'store/wishlist.html', {'wishlist': wishlist})


@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    obj, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        obj.delete()
        action = 'removed'
        msg = f'"{product.name}" retiré des favoris.'
    else:
        action = 'added'
        msg = f'"{product.name}" ajouté aux favoris!'

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'action': action, 'wishlist_count': Wishlist.objects.filter(user=request.user).count()})
    messages.success(request, msg)
    return redirect(request.META.get('HTTP_REFERER', 'store:wishlist'))


def search_view(request):
    q = request.GET.get('q', '')
    products = []
    if q:
        products = Product.objects.filter(
            Q(name__icontains=q) | Q(description__icontains=q),
            is_available=True
        )
    return render(request, 'store/search.html', {'products': products, 'query': q})
