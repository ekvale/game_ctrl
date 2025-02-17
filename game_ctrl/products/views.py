from django.shortcuts import render
from .models import Controller

def home(request):
    featured_controllers = Controller.objects.filter(is_featured=True)
    all_controllers = Controller.objects.all()
    
    context = {
        'featured_controllers': featured_controllers,
        'all_controllers': all_controllers,
    }
    return render(request, 'home.html', context) 