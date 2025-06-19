from django.contrib import admin
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from .models import Product, Category, Tag, ProductTag


class ProductTagInline(admin.TabularInline):
    model = ProductTag
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'slug', 'category', 'price',
        'available', 'discount', 'status',
        'views_count', 'created_at', 'updated'
    ]
    list_filter = ['available', 'category', 'status', 'created_at', 'updated', 'views_count']
    list_editable = ['price', 'available', 'discount', 'status']
    search_fields = ['name', 'descriptions']
    prepopulated_fields = {'slug': ('name',)}
    list_select_related = ['category']
    inlines = [ProductTagInline]
    ordering = ['-views_count', 'name']
    
    actions = ['generate_pdf_report']
    
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
    
    generate_pdf_report.short_description = "Сгенерировать PDF отчет"