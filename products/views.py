from django.shortcuts import render, get_object_or_404
from .models import Category, Controller
from cart.models import Cart
from django.template.loader import get_template
import logging

logger = logging.getLogger(__name__)

def home(request):
    """Homepage view with featured controllers"""
    # Try both possible locations
    possible_templates = [
        '/app/templates/home.html',
        '/app/products/templates/home.html'
    ]
    
    print("DEBUG: Checking template locations:")
    for path in possible_templates:
        try:
            with open(path, 'r') as f:
                print(f"Found template at {path}")
                print("Content preview:", f.read()[:100])
        except FileNotFoundError:
            print(f"No template at {path}")
    
    # Use Django's template loader
    template = get_template('home.html')
    print(f"Django chose template: {template.origin.name}")
    
    context = {
        'featured_controllers': Controller.objects.filter(is_featured=True),
        'categories': Category.objects.all(),
    }
    
    return render(request, 'home.html', context)

def category_detail(request, slug):
    """Category detail view"""
    category = get_object_or_404(Category, slug=slug)
    controllers = Controller.objects.filter(category=category).order_by('-created_at')

    return render(request, 'products/category_detail.html', {
        'category': category,
        'controllers': controllers,
    })

def controller_detail(request, id):
    """Controller detail view"""
    controller = get_object_or_404(Controller, id=id)

    return render(request, 'products/controller_detail.html', {
        'controller': controller,
    })

