from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('produits/', views.product_list, name='product_list'),
    path('produit/<slug:slug>/', views.product_detail, name='product_detail'),
    path('categorie/<slug:slug>/', views.category_detail, name='category'),
    path('genre/<str:genre>/', views.genre_products, name='genre'),
    path('recherche/', views.search_view, name='search'),
    path('panier/', views.cart_view, name='cart'),
    path('panier/ajouter/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('panier/retirer/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('panier/modifier/<int:item_id>/', views.update_cart, name='update_cart'),
    path('favoris/', views.wishlist_view, name='wishlist'),
    path('favoris/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
]
