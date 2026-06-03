from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile, HAITI_DEPARTMENTS


def register(request):
    if request.user.is_authenticated:
        return redirect('store:home')
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        if password1 != password2:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Ce nom d\'utilisateur est déjà pris.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Cet email est déjà utilisé.')
        else:
            user = User.objects.create_user(
                username=username, email=email, password=password1,
                first_name=first_name, last_name=last_name
            )
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, f'Bienvenue {first_name}! Compte créé avec succès.')
            return redirect('store:home')
    return render(request, 'accounts/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('store:home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', 'store:home')
            return redirect(next_url)
        messages.error(request, 'Identifiants incorrects.')
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('store:home')


@login_required
def profile(request):
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        profile_obj.phone = request.POST.get('phone', '')
        profile_obj.address = request.POST.get('address', '')
        profile_obj.city = request.POST.get('city', '')
        profile_obj.department = request.POST.get('department', '')
        if 'avatar' in request.FILES:
            profile_obj.avatar = request.FILES['avatar']
        profile_obj.save()
        messages.success(request, 'Profil mis à jour!')
        return redirect('accounts:profile')
    from orders.models import Order
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    return render(request, 'accounts/profile.html', {
        'profile': profile_obj,
        'departments': HAITI_DEPARTMENTS,
        'recent_orders': recent_orders,
    })
