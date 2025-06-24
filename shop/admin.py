from django.contrib import admin
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from .models import Product, Category, Tag, ProductTag, Review, User
from django.db import models
from simple_history.admin import SimpleHistoryAdmin
from import_export.formats import base_formats
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os


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
    user = fields.Field(column_name='user', attribute='user', widget=ForeignKeyWidget(User, 'username'))
    
    class Meta:
        model = Review
        fields = ('id', 'product', 'user', 'rating', 'text', 'created_at')
        export_order = fields
    
    def get_export_queryset(self):
        """Кастомизация queryset для экспорта"""
        return self.model.objects.select_related('product', 'user').all()


class ProductTagInline(admin.TabularInline):
    model = ProductTag
    extra = 1


@admin.register(Tag)
class TagAdmin(ImportExportModelAdmin):
    resource_class = TagResource
    formats = [base_formats.CSV, base_formats.TSV, base_formats.JSON, base_formats.HTML, base_formats.XLSX]
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
    formats = [base_formats.CSV, base_formats.TSV, base_formats.JSON, base_formats.HTML, base_formats.XLSX]
    list_display = ['name', 'slug', 'products_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    list_filter = ['name']
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug')
        }),
    )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(products_count=models.Count('products'))
        return queryset

    def products_count(self, obj):
        return obj.products_count
    products_count.short_description = 'Количество продуктов'
    products_count.admin_order_field = 'products_count'


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    formats = [base_formats.CSV, base_formats.TSV, base_formats.JSON, base_formats.HTML, base_formats.XLSX]
    list_display = [
        'name', 'slug', 'category', 'price', 'discount_price',
        'available', 'status', 'views_count', 'reviews_count', 'created_at'
    ]
    list_display_links = ['name', 'slug']
    list_filter = ['available', 'category', 'status', 'created_at', 'updated', 'views_count']
    list_editable = ['price', 'available', 'status']
    search_fields = ['name', 'descriptions']
    prepopulated_fields = {'slug': ('name',)}
    list_select_related = ['category']
    inlines = [ProductTagInline]
    ordering = ['-views_count', 'name']
    readonly_fields = ['created_at', 'updated']
    actions = ['generate_pdf_report', 'mark_as_available', 'mark_as_unavailable']
    raw_id_fields = ['category']
    date_hierarchy = 'created_at'
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

    @admin.display(description='Цена со скидкой')
    def discount_price(self, obj):
        return obj.discount_price()

    @admin.display(description='Отзывов')
    def reviews_count(self, obj):
        return obj.reviews.count()
    
    def generate_pdf_report(self, request, queryset):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="products_report.pdf"'

        # Путь к шрифту (Arial или DejaVuSans)
        font_path = 'C:/Windows/Fonts/arial.ttf'
        if not os.path.exists(font_path):
            font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
        pdfmetrics.registerFont(TTFont('CustomFont', font_path))

        p = canvas.Canvas(response, pagesize=letter)
        p.setFont('CustomFont', 12)
        p.drawString(100, 750, "Отчет по продуктам")

        y = 700
        for product in queryset:
            p.drawString(100, y, f"{product.name} - {product.price}₽")
            y -= 20
            if y < 50:
                p.showPage()
                p.setFont('CustomFont', 12)
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
    formats = [base_formats.CSV, base_formats.TSV, base_formats.JSON, base_formats.HTML, base_formats.XLSX]
    list_display = ['user', 'product', 'rating', 'created_at']
    list_filter = ['rating', 'created_at', 'product']
    search_fields = ['user__username', 'text', 'product__name']
    ordering = ['-created_at']
    list_select_related = ['product', 'user']
    filter_horizontal = ['helpful_votes']
    fieldsets = (
        ('Основная информация', {
            'fields': ('product', 'user', 'rating', 'text', 'helpful_votes')
        }),
        ('Метаданные', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at']

admin.site.register(Product.history.model, SimpleHistoryAdmin)
admin.site.register(Category.history.model, SimpleHistoryAdmin)
admin.site.register(Review.history.model, SimpleHistoryAdmin)