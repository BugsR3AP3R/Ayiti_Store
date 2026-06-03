from orders.models import Cart, CartItem
from store.models import Wishlist


def cart_count(request):
    count = 0
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            session_key = request.session.session_key
            if session_key:
                cart = Cart.objects.filter(session_key=session_key).first()
            else:
                cart = None
        if cart:
            count = cart.total_items
    except Exception:
        pass
    return {'cart_count': count}


def wishlist_count(request):
    count = 0
    try:
        if request.user.is_authenticated:
            count = Wishlist.objects.filter(user=request.user).count()
    except Exception:
        pass
    return {'wishlist_count': count}
