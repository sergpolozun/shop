from django.contrib import admin
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from .models import Product, Category, Tag, ProductTag, Review


class TagResource(resources.ModelResource):
    products_count = fields.Field(column_name='products_count', attribute='products_count')
    
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'products_count')
        export_order = fields
    
    def get_export_queryset(self):
        """Кастомизация queryset для экспорта"""
        return self.model.objects.all()
    
    def dehydrate_products_count(self, obj):
        """Кастомизация поля products_count"""
        return obj.products.count()


class ProductResource(resources.ModelResource):
    category = fields.Field(column_name='category', attribute='category', widget=ForeignKeyWidget(Category, 'name'))
    tags = fields.Field(column_name='tags', attribute='tags', widget=ManyToManyWidget(Tag, field='name', separator=', '))
    reviews_count = fields.Field(column_name='reviews_count', attribute='reviews_count')
    average_rating = fields.Field(column_name='average_rating', attribute='average_rating')
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'category', 'price', 'available', 'discount', 'status', 'views_count', 'tags', 'reviews_count', 'average_rating')
        export_order = fields
    
    def get_export_queryset(self):
        """Кастомизация queryset для экспорта"""
        return self.model.objects.select_related('category').prefetch_related('tags', 'reviews').all()
    
    def dehydrate_reviews_count(self, obj):
        """Кастомизация поля reviews_count"""
        return obj.reviews.count()
    
    def dehydrate_average_rating(self, obj):
        """Кастомизация поля average_rating"""
        reviews = obj.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / reviews.count()
        return 0
    
    def get_reviews_count(self, obj):
        """Альтернативный метод для получения количества отзывов"""
        return obj.reviews.count()


class CategoryResource(resources.ModelResource):
    products_count = fields.Field(column_name='products_count', attribute='products_count')
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'products_count')
        export_order = fields
    
    def get_export_queryset(self):
        """Кастомизация queryset для экспорта"""
        return self.model.objects.annotate(products_count=models.Count('products')).all()
    
    def dehydrate_products_count(self, obj):
        """Кастомизация поля products_count"""
        return obj.products.count()


class ReviewResource(resources.ModelResource):
    product = fields.Field(column_name='product', attribute='product', widget=ForeignKeyWidget(Product, 'name'))
    
    class Meta:
        model = Review
        fields = ('id', 'product', 'author', 'rating', 'text', 'created_at')
        export_order = fields
    
    def get_export_queryset(self):
        """Кастомизация queryset для экспорта"""
        return self.model.objects.select_related('product').all()


class ProductTagInline(admin.TabularInline):
    model = ProductTag
    extra = 1


@admin.register(Tag)
class TagAdmin(ImportExportModelAdmin):
    resource_class = TagResource
    list_display = ['name', 'slug', 'products_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    list_filter = ['name']
    
    def products_count(self, obj):
        return obj.products.count()
    products_count.short_description = 'Количество продуктов'


@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    resource_class = CategoryResource
    list_display = ['name', 'slug', 'products_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    list_filter = ['name']
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug')
        }),
        ('Статистика', {
            'fields': ('products_count',),
            'classes': ('collapse',)
        }),
    )
    
    def products_count(self, obj):
        return obj.products.count()
    products_count.short_description = 'Количество продуктов'


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    list_display = [
        'name', 'slug', 'category', 'price', 'discount_price',
        'available', 'status', 'views_count', 'reviews_count', 'created_at'
    ]
    list_filter = ['available', 'category', 'status', 'created_at', 'updated', 'views_count']
    list_editable = ['price', 'available', 'status']
    search_fields = ['name', 'descriptions']
    prepopulated_fields = {'slug': ('name',)}
    list_select_related = ['category']
    inlines = [ProductTagInline]
    ordering = ['-views_count', 'name']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'category', 'descriptions', 'image')
        }),
        ('Цена и скидки', {
            'fields': ('price', 'discount', 'status')
        }),
        ('Статус', {
            'fields': ('available', 'views_count')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['generate_pdf_report', 'mark_as_available', 'mark_as_unavailable']
    
    def discount_price(self, obj):
        return obj.discount_price()
    discount_price.short_description = 'Цена со скидкой'
    
    def reviews_count(self, obj):
        return obj.reviews.count()
    reviews_count.short_description = 'Отзывов'
    
    def generate_pdf_report(self, request, queryset):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="products_report.pdf"'
        
        p = canvas.Canvas(response, pagesize=letter)
        p.drawString(100, 750, "Отчет по продуктам")
        
        y = 700
        for product in queryset:
            p.drawString(100, y, f"{product.name} - {product.price}₽")
            y -= 20
            if y < 50:
                p.showPage()
                y = 750
        
        p.showPage()
        p.save()
        return response
    
    def mark_as_available(self, request, queryset):
        queryset.update(available=True)
    mark_as_available.short_description = "Отметить как доступные"
    
    def mark_as_unavailable(self, request, queryset):
        queryset.update(available=False)
    mark_as_unavailable.short_description = "Отметить как недоступные"
    
    generate_pdf_report.short_description = "Сгенерировать PDF отчет"


@admin.register(Review)
class ReviewAdmin(ImportExportModelAdmin):
    resource_class = ReviewResource
    list_display = ['author', 'product', 'rating', 'created_at']
    list_filter = ['rating', 'created_at', 'product']
    search_fields = ['author', 'text', 'product__name']
    ordering = ['-created_at']
    list_select_related = ['product']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('product', 'author', 'rating', 'text')
        }),
        ('Метаданные', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )