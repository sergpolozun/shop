from shop.models import Product
from django import template

register = template.Library()
# простой тег


@register.simple_tag
def current_year():
    from datetime import datetime
    return datetime.now().year
# тег с контекстными переменными


@register.simple_tag(takes_context=True)
def show_user_greeting(context):
    user = context['request'].user
    if user.is_authenticated:
        return f"Привет, {user.username}!"
    return "Привет, гость!"


#тег, возвращающий набор запросов


@register.simple_tag
def get_popular_products(limit=5):
    return Product.objects.filter(available=True).order_by('-created_at')[:limit]
