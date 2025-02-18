from django.shortcuts import render, get_object_or_404
from .models import Category, Controller
from cart.models import Cart
from django.template.loader import get_template
import logging

logger = logging.getLogger(__name__)

def home(request):
    """Homepage view with featured controllers"""
    template = get_template('home.html')
    logger.info(f"Using template from: {template.origin.name}")
    
    # Add debug info to context
    context = {
        'debug_info': {
            'template_path': template.origin.name,
            'template_exists': template.origin.exists,
            'template_content': open(template.origin.name).read()[:100]  # First 100 chars
        }
    }
    
    # Add your existing context
    context.update({
        'featured_controllers': Controller.objects.filter(is_featured=True),
        'categories': Category.objects.all(),
    })
    
    # Print debug info to console
    print("DEBUG: Template Info:", context['debug_info'])
    
    # Add cart to context if user is authenticated
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            context['cart'] = cart
        except Cart.DoesNotExist:
            pass
            
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

