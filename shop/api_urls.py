from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import ProductViewSet, CategoryViewSet, ReviewViewSet, TagViewSet
from . import views

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'tags', TagViewSet)

urlpatterns = [
    path('terminal/sales/', views.api_terminal_sales, name='api_terminal_sales'),
    path('terminal/news/', views.api_terminal_news, name='api_terminal_news'),
    path('terminal/popular/', views.api_terminal_popular, name='api_terminal_popular'),
    path('', include(router.urls)),
] 