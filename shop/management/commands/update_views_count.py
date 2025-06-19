from django.core.management.base import BaseCommand
from django.db.models import Count
from shop.models import Product, ProductView


class Command(BaseCommand):
    help = 'Обновляет счетчик просмотров товаров на основе данных из ProductView'

    def handle(self, *args, **options):
        self.stdout.write('Начинаю обновление счетчиков просмотров...')
        
        # Получаем количество просмотров для каждого товара
        view_counts = ProductView.objects.values('product').annotate(
            total_views=Count('id')
        )
        
        updated_count = 0
        
        for view_data in view_counts:
            product_id = view_data['product']
            total_views = view_data['total_views']
            
            try:
                product = Product.objects.get(id=product_id)
                product.views_count = total_views
                product.save(update_fields=['views_count'])
                updated_count += 1
                self.stdout.write(f'Обновлен товар {product.name}: {total_views} просмотров')
            except Product.DoesNotExist:
                self.stdout.write(f'Товар с ID {product_id} не найден')
        
        self.stdout.write(
            self.style.SUCCESS(f'Успешно обновлено {updated_count} товаров')
        ) 