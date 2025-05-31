from django.db import models
from django.urls import reverse
from django.utils import timezone


# --- Кастомный менеджер ---
class AvailableManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(available=True)


# --- Категория ---
class Category(models.Model):
    name = models.CharField(max_length=20, unique=True)
    slug = models.SlugField(max_length=20, unique=True)

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
        return reverse("shop:product_detail", args=[self.slug])

    def discount_price(self):
        if self.discount:
            return round(self.price - self.price * self.discount / 100, 2)
        return self.price
