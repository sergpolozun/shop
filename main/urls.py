from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.desktop_view, name='desktop'),
]
