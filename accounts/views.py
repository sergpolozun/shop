from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from shop.models import CartItem, Product
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('shop:product_list')
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

@login_required
def profile(request):
    user = request.user
    password_changed = False
    if request.method == 'POST':
        user.email = request.POST.get('email', user.email)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.save()
        # обработка смены пароля только если хотя бы одно поле заполнено
        if request.POST.get('old_password') or request.POST.get('new_password1') or request.POST.get('new_password2'):
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                password_changed = True
        else:
            password_form = PasswordChangeForm(user)
        # редирект после сохранения
        return redirect('shop:product_list')
    else:
        password_form = PasswordChangeForm(user)
    return render(request, 'accounts/profile.html', {
        'user': user,
        'password_form': password_form,
        'password_changed': password_changed,
    })
