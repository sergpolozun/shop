from django.shortcuts import render

def desktop_view(request):
    # Использование сессий Django
    if 'visit_count' not in request.session:
        request.session['visit_count'] = 0
    request.session['visit_count'] += 1
    
    # Сохраняем информацию о последнем посещении
    request.session['last_visit'] = str(request.session.get('visit_count'))
    
    context = {
        'visit_count': request.session['visit_count'],
        'last_visit': request.session.get('last_visit'),
    }
    
    return render(request, 'main/index/index.html', context)
