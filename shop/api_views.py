from rest_framework import generics, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg, Count
from .models import Product, Category, Review, Tag
from .serializers import (
    ProductSerializer, ProductDetailSerializer, CategorySerializer,
    ReviewSerializer, TagSerializer
)


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'available', 'status', 'price']
    search_fields = ['name', 'descriptions']
    ordering_fields = ['name', 'price', 'created_at', 'views_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer
    
    def get_queryset(self):
        queryset = Product.objects.select_related('category').prefetch_related('tags', 'reviews')
        
        # Фильтрация по цене
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Фильтрация по рейтингу
        min_rating = self.request.query_params.get('min_rating')
        if min_rating:
            queryset = queryset.annotate(avg_rating=Avg('reviews__rating')).filter(avg_rating__gte=min_rating)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Получить популярные продукты по количеству просмотров"""
        popular_products = self.get_queryset().order_by('-views_count')[:10]
        serializer = self.get_serializer(popular_products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def discounted(self, request):
        """Получить продукты со скидкой"""
        discounted_products = self.get_queryset().filter(discount__gt=0)
        serializer = self.get_serializer(discounted_products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_review(self, request, pk=None):
        """Добавить отзыв к продукту"""
        product = self.get_object()
        serializer = ReviewSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def increment_views(self, request, pk=None):
        """Увеличить счетчик просмотров"""
        product = self.get_object()
        product.views_count += 1
        product.save()
        return Response({'message': 'Просмотры увеличены'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def special_filter(self, request):
        """(скидка > 0 ИЛИ статус 'new') И НЕ категория 'Архив'"""
        q_or = Q(discount__gt=0) | Q(status='new')
        q_not = ~Q(category__name='Архив')
        products = Product.objects.filter(q_or & q_not)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def cheap_or_popular_not_sale(self, request):
        """(цена < 1000 ИЛИ просмотров > 100) И НЕ статус 'sale'"""
        q_or = Q(price__lt=1000) | Q(views_count__gt=100)
        q_not = ~Q(status='sale')
        products = Product.objects.filter(q_or & q_not)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Получить все продукты категории"""
        category = self.get_object()
        products = category.products.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'rating']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def top_rated(self, request):
        """Получить отзывы с высоким рейтингом"""
        top_reviews = self.get_queryset().filter(rating__gte=4).order_by('-rating', '-created_at')
        serializer = self.get_serializer(top_reviews, many=True)
        return Response(serializer.data)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Получить все продукты с данным тегом"""
        tag = self.get_object()
        products = tag.products.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data) 