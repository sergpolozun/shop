from django.shortcuts import render

# Create your views here.

def paint_editor(request):
    """Представление для графического редактора"""
    return render(request, 'paint/editor.html')
