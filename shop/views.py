from django.shortcuts import render
from .models import Product, Category


def product_list(request):
    category_id = request.GET.get('category')
    categories = Category.objects.all()
    products = Product.objects.all()

    if category_id:
        try:
            category_id = int(category_id)
            products = products.filter(category_id=category_id)
        except ValueError:
            category_id = None

    return render(request, 'shop/product/list.html', {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
    })
