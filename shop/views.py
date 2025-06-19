from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Q, Min, Max, Avg
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category, Tag, Review, ProductLink, ProductView, CartItem, Favorite
from .forms import ProductForm, CategoryForm
from django.db.models import Avg
from django.utils import timezone
import json
from django.urls import reverse
from django.middleware.csrf import get_token


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
    
    # Пагинация
    paginator = Paginator(products, 20)  # 20 товаров на страницу
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    categories = Category.objects.all()
    
    favorite_ids = []
    if request.user.is_authenticated:
        favorite_ids = list(Favorite.objects.filter(user=request.user).values_list('product_id', flat=True))
    
    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category_id,
        'current_sort': sort_by,
        'current_order': order,
        'current_min_price': min_price,
        'current_max_price': max_price,
        'price_stats': price_stats,
        'favorite_ids': favorite_ids,
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
    
    # Проверяем, есть ли товар в корзине
    cart_quantity = 0
    if request.user.is_authenticated:
        try:
            cart_item = CartItem.objects.get(user=request.user, product=product)
            cart_quantity = cart_item.quantity
        except CartItem.DoesNotExist:
            pass
    else:
        cart = request.session.get('cart', {})
        cart_quantity = cart.get(str(product.id), 0)
    
    # Проверяем, есть ли товар в избранном
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, product=product).exists()
    
    # Определяем статус товара
    status_text = ""
    if product.status == 'sale':
        status_text = '<span class="product-status-sale">Распродажа</span>'
    elif product.status == 'new':
        status_text = '<span class="product-status-new">Новый</span>'
    # Если статус обычный — ничего не выводим
    
    # Формируем HTML для модального окна
    if product.image:
        image_html = f'<img src="{product.image.url}" alt="{product.name}" class="product-detail-image">'
    else:
        image_html = '<img src="/static/img/notfound.jpg" alt="Нет фото" class="product-detail-image">'
    
    # Формируем HTML для цены с учетом скидки
    if product.discount > 0:
        price_html = f"""
        <p class="price">
            <span class="old-price">{product.price} ₽</span>
            <span class="discount-price">{product.discount_price()} ₽</span>
            <span class="discount-badge">-{product.discount}%</span>
        </p>
        """
    else:
        price_html = f'<p class="price">{product.price} ₽</p>'
    
    # Формируем HTML для кнопки/формы в зависимости от наличия в корзине
    if cart_quantity > 0:
        # Товар уже в корзине - показываем форму с количеством
        cart_html = f"""
        <form method="post" action="/shop/cart/add/{product.id}/" style="display:inline;white-space:nowrap;" id="updateForm_{product.id}">
            <input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">
            <button type="button" onclick="changeQtyModal(this, -1)" class="btn-win98 btn-qty">−</button>
            <input type="number" name="quantity" value="{cart_quantity}" class="cart-qty-input-win98 no-arrows" min="1" style="width:56px;" data-price="{product.price}">
            <button type="button" onclick="changeQtyModal(this, 1)" class="btn-win98 btn-qty">+</button>
        </form>
        """
    else:
        # Товар не в корзине - показываем кнопку добавления
        cart_html = f"""
        <button class="btn-win98" onclick="addToCartSimple({product.id})">Добавить в корзину</button>
        """
    
    # Формируем HTML для кнопки избранного
    favorite_text = "Удалить из избранного" if is_favorite else "Добавить в избранное"
    favorite_class = "btn-win98 favorite-active" if is_favorite else "btn-win98"
    favorite_html = f"""
    <button class="{favorite_class}" onclick="toggleFavoriteModal({product.id}, this)">{favorite_text}</button>
    """
    
    html_content = f"""
    <div class="product-detail-win98">
        <div class="product-image-container">
            {image_html}
        </div>
        <div class="product-info">
            <h4>{product.name}</h4>
            {price_html}
            <p class="description">{product.descriptions}</p>
            <p class="category">Категория: {product.category.name}</p>
            <p class="created">Добавлен: {product.created_at.strftime('%d.%m.%Y')}</p>
            {status_text}
            <div class="product-actions">
                {cart_html}
                {favorite_html}
            </div>
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


def cart_view(request):
    if request.user.is_authenticated:
        cart_items_qs = CartItem.objects.filter(user=request.user).select_related('product')
        cart_items = []
        total = 0
        for item in cart_items_qs:
            subtotal = item.product.price * item.quantity
            total += subtotal
            cart_items.append({
                'product': item.product,
                'quantity': item.quantity,
                'subtotal': subtotal
            })
        return render(request, 'shop/cart.html', {
            'cart_items': cart_items,
            'total': total
        })
    else:
        cart = request.session.get('cart', {})
        product_ids = cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart_items = []
        total = 0
        for product in products:
            quantity = cart.get(str(product.id), 0)
            subtotal = product.price * quantity
            total += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
        return render(request, 'shop/cart.html', {
            'cart_items': cart_items,
            'total': total
        })


def cart_add(request, product_id):
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity < 1:
                quantity = 1
        except (ValueError, TypeError):
            quantity = 1
        
        if request.user.is_authenticated:
            product = get_object_or_404(Product, id=product_id)
            cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
            # Если товар уже был в корзине, заменяем количество, иначе устанавливаем
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart = request.session.get('cart', {})
            cart[str(product_id)] = quantity
            request.session['cart'] = cart
        
        return JsonResponse({'success': True, 'message': f'Товар добавлен в корзину (количество: {quantity})'})
    else:
        # Для GET-запросов оставляем старую логику
        if request.user.is_authenticated:
            product = get_object_or_404(Product, id=product_id)
            cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
            if not created:
                cart_item.quantity += 1
                cart_item.save()
            return redirect(request.META.get('HTTP_REFERER', reverse('shop:cart')))
        else:
            cart = request.session.get('cart', {})
            cart[str(product_id)] = cart.get(str(product_id), 0) + 1
            request.session['cart'] = cart
            return redirect(request.META.get('HTTP_REFERER', reverse('shop:cart')))


def cart_remove(request, product_id):
    if request.user.is_authenticated:
        CartItem.objects.filter(user=request.user, product_id=product_id).delete()
        return redirect('shop:cart')
    else:
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            del cart[str(product_id)]
            request.session['cart'] = cart
        return redirect('shop:cart')


def cart_clear(request):
    if request.user.is_authenticated:
        CartItem.objects.filter(user=request.user).delete()
        return redirect('shop:cart')
    else:
        request.session['cart'] = {}
        return redirect('shop:cart')


def cart_update(request, product_id):
    if request.method == 'POST':
        if request.user.is_authenticated:
            try:
                quantity = int(request.POST.get('quantity', 1))
                if quantity < 1:
                    quantity = 1
                cart_item, created = CartItem.objects.get_or_create(user=request.user, product_id=product_id)
                cart_item.quantity = quantity
                cart_item.save()
            except (ValueError, TypeError):
                pass
            return redirect('shop:cart')
        else:
            cart = request.session.get('cart', {})
            try:
                quantity = int(request.POST.get('quantity', 1))
                if quantity < 1:
                    quantity = 1
                cart[str(product_id)] = quantity
                request.session['cart'] = cart
            except (ValueError, TypeError):
                pass
            return redirect('shop:cart')
    return redirect('shop:cart')


@login_required
def favorite_toggle(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    fav, created = Favorite.objects.get_or_create(user=request.user, product=product)
    if not created:
        fav.delete()
        return JsonResponse({'status': 'removed'})
    return JsonResponse({'status': 'added'})


@login_required
def favorite_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('product')
    products = [fav.product for fav in favorites]
    categories = Category.objects.all()
    
    # Получаем ID избранных товаров для правильного отображения
    favorite_ids = list(Favorite.objects.filter(user=request.user).values_list('product_id', flat=True))
    
    # Пагинация для избранных товаров
    paginator = Paginator(products, 20)  # 20 товаров на страницу
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'favorite_page': True,
        'favorite_ids': favorite_ids,
    }
    return render(request, 'shop/product/favorite.html', context)
