from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('paiement/<str:order_number>/', views.payment, name='payment'),
    path('confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),
    path('mes-commandes/', views.order_list, name='order_list'),
    path('commande/<str:order_number>/', views.order_detail, name='order_detail'),
]
