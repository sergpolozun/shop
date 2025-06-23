from rest_framework import serializers
from .models import Product, Category, Review, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'products_count']
    
    def get_products_count(self, obj):
        return obj.products.count()


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.CharField(max_length=100)
    
    class Meta:
        model = Review
        fields = ['id', 'product', 'author', 'rating', 'text', 'created_at']
        read_only_fields = ['created_at']
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Рейтинг должен быть от 1 до 5")
        return value


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    tags = TagSerializer(many=True, read_only=True)
    reviews_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    discount_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'category_id', 'image', 
            'descriptions', 'price', 'available', 'created_at', 'updated',
            'discount', 'status', 'views_count', 'tags', 'reviews_count',
            'average_rating', 'discount_price'
        ]
        read_only_fields = ['slug', 'created_at', 'updated', 'views_count']
    
    def get_reviews_count(self, obj):
        return obj.reviews.count()
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / reviews.count()
        return 0
    
    def get_discount_price(self, obj):
        return obj.discount_price()
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Цена должна быть больше нуля")
        return value
    
    def validate_discount(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Скидка должна быть от 0 до 100 процентов")
        return value

    def validate_name(self, value):
        if Product.objects.filter(name=value).exists():
            raise serializers.ValidationError("Товар с таким названием уже существует.")
        return value

    def validate_tags(self, value):
        if len(value) > 5:
            raise serializers.ValidationError("Можно выбрать не более 5 тегов для товара.")
        return value


class ProductDetailSerializer(ProductSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    
    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['reviews'] 