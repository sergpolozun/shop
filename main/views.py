from django.shortcuts import render

def desktop_view(request):
    return render(request, 'main/index/index.html')
