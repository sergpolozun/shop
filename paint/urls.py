from django.urls import path
from . import views

app_name = 'paint'

urlpatterns = [
    path('', views.paint_editor, name='editor'),
] 