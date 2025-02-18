from django.shortcuts import render, get_object_or_404
from .models import Category, Controller

def home(request):
    """Homepage view with featured controllers"""
    featured_controllers = Controller.objects.filter(is_featured=True, available=True)
    categories = Category.objects.all()
    
    context = {
        'featured_controllers': featured_controllers,
        'categories': categories,
    }
    return render(request, 'products/home.html', context)

def category_detail(request, slug):
    """Category detail view"""
    category = get_object_or_404(Category, slug=slug)
    controllers = Controller.objects.filter(category=category).order_by('-created_at')

    return render(request, 'products/category_detail.html', {
        'category': category,
        'controllers': controllers,
    })

def controller_detail(request, slug):
    """Controller detail view"""
    controller = get_object_or_404(Controller, slug=slug)

    return render(request, 'products/controller_detail.html', {
        'controller': controller,
    })

