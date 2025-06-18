from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Q, Min, Max, Avg
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category, Tag, Review, ProductLink, ProductView
from .forms import ProductForm, CategoryForm
from django.db.models import Avg
from django.utils import timezone
import json


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def product_list(request):
    # Получаем параметры фильтрации
    sort_by = request.GET.get('sort', 'popularity')  # По умолчанию по популярности
    order = request.GET.get('order', 'desc')  # По умолчанию убывание
    category_id = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    # Базовый queryset
    products = Product.objects.all()
    
    # Фильтрация по категории
    if category_id and category_id != 'all' and category_id != 'None':
        try:
            category_id = int(category_id)
            products = products.filter(category_id=category_id)
        except (ValueError, TypeError):
            # Если category_id не является числом, игнорируем фильтрацию
            pass
    
    # Фильтрация по диапазону цен
    if min_price:
        try:
            min_price = float(min_price)
            products = products.filter(price__gte=min_price)
        except (ValueError, TypeError):
            pass
    
    if max_price:
        try:
            max_price = float(max_price)
            products = products.filter(price__lte=max_price)
        except (ValueError, TypeError):
            pass
    
    # Получаем статистику цен для текущей выборки
    price_stats = products.aggregate(
        min_price=Min('price'),
        max_price=Max('price'),
        avg_price=Avg('price')
    )
    
    # Сортировка
    if sort_by == 'popularity':
        products = products.annotate(view_count=Count('views')).order_by(
            '-view_count' if order == 'desc' else 'view_count'
        )
    elif sort_by == 'price':
        products = products.order_by(
            '-price' if order == 'desc' else 'price'
        )
    elif sort_by == 'date':
        products = products.order_by(
            '-created_at' if order == 'desc' else 'created_at'
        )
    elif sort_by == 'name':
        products = products.order_by(
            '-name' if order == 'desc' else 'name'
        )
    
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'current_category': category_id,
        'current_sort': sort_by,
        'current_order': order,
        'current_min_price': min_price,
        'current_max_price': max_price,
        'price_stats': price_stats,
    }
    
    return render(request, 'shop/product/list.html', context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    # Отслеживаем просмотр
    ip_address = get_client_ip(request)
    ProductView.objects.get_or_create(
        product=product,
        ip_address=ip_address,
        defaults={'viewed_at': timezone.now()}
    )
    
    # Получаем связанные товары
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(pk=product.pk)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'shop/product/detail.html', context)


def product_detail_json(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    # Отслеживаем просмотр
    ip_address = get_client_ip(request)
    ProductView.objects.get_or_create(
        product=product,
        ip_address=ip_address,
        defaults={'viewed_at': timezone.now()}
    )
    
    # Формируем HTML для модального окна
    html_content = f"""
    <div class="product-detail-win98">
        <div class="product-image-container">
            {f'<img src="{product.image.url}" alt="{product.name}" class="product-detail-image">' if product.image else '<div class="no-image-large">Нет фото</div>'}
        </div>
        <div class="product-info">
            <h4>{product.name}</h4>
            <p class="price">{product.price} ₽</p>
            <p class="description">{product.descriptions}</p>
            <p class="category">Категория: {product.category.name}</p>
            <p class="created">Добавлен: {product.created_at.strftime('%d.%m.%Y')}</p>
        </div>
    </div>
    """
    
    return JsonResponse({
        'name': product.name,
        'html': html_content
    })


@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.save()
            form.save_m2m()  # Сохраняем many-to-many связи
            messages.success(request, 'Продукт успешно создан!')
            return HttpResponseRedirect(product.get_absolute_url())
    else:
        form = ProductForm()
    
    return render(request, 'shop/product/form.html', {
        'form': form,
        'title': 'Создать продукт'
    })


@login_required
def product_edit(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Продукт успешно обновлен!')
            return HttpResponseRedirect(product.get_absolute_url())
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'shop/product/form.html', {
        'form': form,
        'product': product,
        'title': 'Редактировать продукт'
    })


@login_required
def product_delete(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Продукт успешно удален!')
        return redirect('shop:product_list')
    
    return render(request, 'shop/product/delete_confirm.html', {
        'product': product
    })


def product_stats(request):
    # Примеры использования различных методов QuerySet
    total_products = Product.objects.count()
    available_products = Product.objects.filter(available=True).count()
    
    # Использование values() и values_list()
    category_stats = Category.objects.annotate(
        product_count=Count('products')
    ).values('name', 'product_count')
    
    price_stats = Product.objects.values_list('price', flat=True)
    
    # Использование exists()
    has_discounted_products = Product.objects.filter(discount__gt=0).exists()
    
    # Использование update()
    # Product.objects.filter(status='new').update(status='std')
    
    return render(request, 'shop/product/stats.html', {
        'total_products': total_products,
        'available_products': available_products,
        'category_stats': category_stats,
        'price_stats': price_stats,
        'has_discounted_products': has_discounted_products,
    })
