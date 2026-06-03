from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Order, OrderItem, Cart, CartItem, ShippingTracking
from store.models import Product
from accounts.models import UserProfile, HAITI_DEPARTMENTS


def checkout(request):
    cart = None
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        sk = request.session.session_key
        if sk:
            cart = Cart.objects.filter(session_key=sk).first()

    if not cart or cart.total_items == 0:
        messages.warning(request, 'Votre panier est vide.')
        return redirect('store:cart')

    items = cart.cart_items.select_related('product').all()
    shipping_cost = 500 if cart.subtotal < 5000 else 0
    total = cart.subtotal + shipping_cost

    profile = None
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        city = request.POST.get('city', '')
        department = request.POST.get('department', '')
        payment_method = request.POST.get('payment_method', '')

        if not all([first_name, last_name, email, phone, address, city, department, payment_method]):
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
        else:
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_key=request.session.session_key or '',
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                address=address,
                city=city,
                department=department,
                payment_method=payment_method,
                subtotal=cart.subtotal,
                shipping_cost=shipping_cost,
                total=total,
                notes=request.POST.get('notes', ''),
            )
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    variant=item.variant,
                    product_name=item.product.name,
                    product_price=item.unit_price,
                    quantity=item.quantity,
                    size=item.size,
                    color=item.color,
                )
            ShippingTracking.objects.create(
                order=order,
                status='pending',
                description='Commande reçue et en attente de confirmation.',
            )
            cart.cart_items.all().delete()
            return redirect('orders:payment', order_number=order.order_number)

    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'items': items,
        'shipping_cost': shipping_cost,
        'total': total,
        'profile': profile,
        'departments': HAITI_DEPARTMENTS,
    })


def payment(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    if request.method == 'POST':
        payment_ref = request.POST.get('payment_ref', '')
        payment_phone = request.POST.get('payment_phone', '')
        if order.payment_method == 'cash':
            order.payment_status = 'pending'
            order.status = 'confirmed'
        else:
            order.payment_id = payment_ref
            order.payment_status = 'paid'
            order.payment_date = timezone.now()
            order.status = 'confirmed'
        order.save()
        ShippingTracking.objects.create(
            order=order,
            status='confirmed',
            description=f'Paiement reçu via {order.get_payment_method_display()}. Commande confirmée.',
        )
        messages.success(request, f'Paiement confirmé! Commande #{order.order_number}')
        return redirect('orders:order_confirmation', order_number=order.order_number)

    return render(request, 'orders/payment.html', {'order': order})


def order_confirmation(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'orders/confirmation.html', {'order': order})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    tracking = order.tracking.all()
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'tracking': tracking,
    })
