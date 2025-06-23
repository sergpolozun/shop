from django.urls import path, include
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/<int:pk>/detail/', views.product_detail_json, name='product_detail_json'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('cart/clear/', views.cart_clear, name='cart_clear'),
    path('product/new/', views.product_create, name='product_create'),
    path('product/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('product/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('product/<int:pk>/stats/', views.product_stats, name='product_stats'),
    path('favorite/toggle/<int:product_id>/', views.favorite_toggle, name='favorite_toggle'),
    path('favorite/', views.favorite_list, name='favorite_list'),
    path('product/<int:product_id>/review/', views.add_review, name='add_review'),
    path('product/<int:product_id>/reviews/', views.get_reviews, name='get_reviews'),
    path('product/<int:product_id>/review-form/', views.get_review_form, name='get_review_form'),
    path('category/<int:category_id>/', views.product_list_by_category, name='product_list_by_category'),
    # API URLs
    path('api/', include('shop.api_urls')),
]
