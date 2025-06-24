from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords


# --- Кастомный менеджер ---
class AvailableManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(available=True)


# --- Теги для продуктов ---
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    
    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
    
    def __str__(self):
        return self.name


# --- Промежуточная модель для связи продуктов и тегов ---
class ProductTag(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['product', 'tag']
        verbose_name = 'Тег продукта'
        verbose_name_plural = 'Теги продуктов'


# --- Категория ---
class Category(models.Model):
    name = models.CharField(max_length=20, unique=True)
    slug = models.SlugField(max_length=20, unique=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['name'])]
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


# --- Продукт ---
class Product(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('sale', 'Распродажа'),
        ('std', 'Обычный'),
    ]

    category = models.ForeignKey(Category,
                                 related_name='products',
                                 on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    image = models.ImageField(upload_to='products/%Y/%m/%d',
                              blank=True)
    descriptions = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    discount = models.DecimalField(default=0.00, max_digits=4, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='std')
    views_count = models.PositiveIntegerField(default=0, verbose_name='Количество просмотров')
    history = HistoricalRecords()
    
    # ManyToManyField с параметром through
    tags = models.ManyToManyField(Tag, through=ProductTag, related_name='products')

    # --- Менеджеры ---
    objects = models.Manager()        # стандартный
    available_products = AvailableManager()  # кастомный

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
            models.Index(fields=['-created_at']),
        ]
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("shop:product_detail", args=[self.pk])

    def discount_price(self):
        if self.discount:
            return round(self.price - self.price * self.discount / 100, 2)
        return self.price

    def save(self, *args, **kwargs):
        # Кастомная логика сохранения
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# --- Отзывы о продуктах (ManyToManyField без through) ---
class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 звезда'),
        (2, '2 звезды'),
        (3, '3 звезды'),
        (4, '4 звезды'),
        (5, '5 звезд'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()
    
    # ManyToManyField без through
    helpful_votes = models.ManyToManyField('auth.User', related_name='helpful_reviews')
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
        unique_together = ['product', 'user']
    
    def __str__(self):
        return f'Отзыв от {self.user.username} на {self.product.name}'


class ProductFile(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='product_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Файл продукта'
        verbose_name_plural = 'Файлы продуктов'

    def __str__(self):
        return f'Файл для {self.product.name}'


class ProductLink(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='links')
    url = models.URLField()
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Ссылка на продукт'
        verbose_name_plural = 'Ссылки на продукт'

    def __str__(self):
        return f'Ссылка для {self.product.name}'


# --- Отслеживание просмотров продуктов ---
class ProductView(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='views')
    ip_address = models.GenericIPAddressField()
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Просмотр продукта'
        verbose_name_plural = 'Просмотры продуктов'
        unique_together = ['product', 'ip_address', 'viewed_at']
    
    def __str__(self):
        return f'Просмотр {self.product.name} с {self.ip_address}'


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Корзина пользователей'

    def __str__(self):
        return f"{self.product.name} x{self.quantity} для {self.user.username}"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        verbose_name = 'Избранный товар'
        verbose_name_plural = 'Избранные товары'

    def __str__(self):
        return f"{self.product.name} в избранном у {self.user.username}"
