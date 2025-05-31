from django.contrib import admin
from .models import Product, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'slug', 'category', 'price',
        'available', 'discount', 'status',
        'created_at', 'updated'
    ]
    list_filter = ['available', 'category', 'status', 'created_at', 'updated']
    list_editable = ['price', 'available', 'discount', 'status']
    search_fields = ['name', 'descriptions']
    prepopulated_fields = {'slug': ('name',)}
    list_select_related = ['category']