from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from shop.models import CartItem, Product
from django.db import transaction

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('shop')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

class CustomLoginView(LoginView):
    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        session_cart = self.request.session.get('cart', {})
        if user.is_authenticated and session_cart:
            with transaction.atomic():
                for product_id, quantity in session_cart.items():
                    try:
                        product = Product.objects.get(id=product_id)
                        cart_item, created = CartItem.objects.get_or_create(user=user, product=product)
                        if not created:
                            cart_item.quantity += quantity
                        else:
                            cart_item.quantity = quantity
                        cart_item.save()
                    except Product.DoesNotExist:
                        continue
            self.request.session['cart'] = {}
        return response
