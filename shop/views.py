from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from .models import Product, Category
from django.db.models import Avg


def product_list(request):
    category_id = request.GET.get('category')
    categories = Category.objects.annotate(product_count=Count('products'))
    c = Category.objects.aggregate(product_avg=Avg("products", default=0))

    products = Product.available_products.all()

    if category_id:
        try:
            category_id = int(category_id)
            selected_category = get_object_or_404(Category, id=category_id)
            products = products.filter(category__id=category_id)

            products = products.exclude(discount__gte=100)

        except (ValueError, Category.DoesNotExist):
            selected_category = None
    else:
        selected_category = None

    products = products.order_by('-created_at')

    paginator = Paginator(products, 30)
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'shop/product/list.html', {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'shop/product/detail.html', {'product': product})
