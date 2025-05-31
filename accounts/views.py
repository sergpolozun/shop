from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth import login

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
