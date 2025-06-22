from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import ProductViewSet, CategoryViewSet, ReviewViewSet, TagViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'tags', TagViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
] 