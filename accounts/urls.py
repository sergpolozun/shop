from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView



urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='shop'), name='logout'),
    path('register/', views.register, name='register'),

]
