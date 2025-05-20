from django.urls import path
from . import views

urlpatterns = [
    path('', views.desktop_view, name='desktop'),
]
