from django import forms
from .models import Product, Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'descriptions', 'price', 'available', 'discount', 'status', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название продукта'}),
            'descriptions': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Описание продукта'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Название',
            'category': 'Категория',
            'descriptions': 'Описание',
            'price': 'Цена',
            'available': 'Доступен',
            'discount': 'Скидка (%)',
            'status': 'Статус',
            'image': 'Изображение',
        }
        help_texts = {
            'name': 'Введите название продукта',
            'descriptions': 'Подробное описание продукта',
            'price': 'Цена в рублях',
            'discount': 'Скидка в процентах (0-100)',
        }
        error_messages = {
            'name': {
                'required': 'Название обязательно для заполнения',
                'max_length': 'Название не может быть длиннее 50 символов',
            },
            'price': {
                'required': 'Цена обязательна для заполнения',
                'min_value': 'Цена должна быть больше 0',
            },
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price <= 0:
            raise forms.ValidationError('Цена должна быть больше 0')
        return price

    def clean_discount(self):
        discount = self.cleaned_data.get('discount')
        if discount and (discount < 0 or discount > 100):
            raise forms.ValidationError('Скидка должна быть от 0 до 100 процентов')
        return discount

    def save(self, commit=True):
        product = super().save(commit=False)
        # Дополнительная обработка перед сохранением
        if product.price and product.price < 0:
            raise forms.ValidationError('Цена не может быть отрицательной')
        if commit:
            product.save()
            self.save_m2m()
        return product


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
        } 