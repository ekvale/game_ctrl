from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.cache import never_cache
from django.core.exceptions import ValidationError
from django.utils.html import escape
from django_ratelimit.decorators import ratelimit
import logging
import re
from .models import Cart, CartItem
from products.models import Controller
from django.conf import settings
from django.db.models import Sum
from .cart import Cart
from .forms import CartAddProductForm

logger = logging.getLogger('game_ctrl.cart')

# Add constants
MAX_CART_ITEMS = 20  # Maximum total items in cart
MAX_ITEM_PRICE = 10000  # Maximum price in dollars
MAX_TOTAL_PRICE = 20000  # Maximum cart total

def sanitize_input(value):
    """Sanitize user input"""
    if not value:
        return value
    # Convert to string if not already
    value = str(value)
    # Remove any non-alphanumeric characters except basic punctuation
    value = re.sub(r'[^a-zA-Z0-9\s\-_\.,]', '', value)
    # Escape HTML
    return escape(value)

def validate_quantity(quantity):
    """Validate quantity input"""
    try:
        quantity = int(quantity)
        if quantity < 0:
            raise ValidationError("Quantity must be positive")
        if quantity > 10:
            raise ValidationError("Maximum quantity exceeded")
        return quantity
    except (TypeError, ValueError):
        raise ValidationError("Invalid quantity format")

def validate_cart_limits(cart, new_quantity=0):
    """Validate cart limits"""
    # Check total number of items
    total_items = cart.items.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_items += new_quantity
    
    if total_items > MAX_CART_ITEMS:
        raise ValidationError(f"Cart cannot exceed {MAX_CART_ITEMS} items")
        
    # Check total price
    cart_total = sum(item.total_price for item in cart.items.all())
    if cart_total > MAX_TOTAL_PRICE:
        raise ValidationError(f"Cart total cannot exceed ${MAX_TOTAL_PRICE}")

def validate_controller(controller):
    """Validate controller"""
    if not controller.is_active:
        raise ValidationError("Product is not available")
        
    if controller.price > MAX_ITEM_PRICE:
        raise ValidationError(f"Item price cannot exceed ${MAX_ITEM_PRICE}")
        
    # Add stock validation if you have stock tracking
    if hasattr(controller, 'stock') and controller.stock <= 0:
        raise ValidationError("Item is out of stock")

def validate_request_origin(request):
    """Validate request origin"""
    referer = request.META.get('HTTP_REFERER', '')
    if not referer:
        raise ValidationError("Missing referer")
        
    allowed_hosts = settings.ALLOWED_HOSTS
    if not any(host in referer for host in allowed_hosts):
        raise ValidationError("Invalid request origin")

@login_required
@never_cache
@ratelimit(key='user', rate='30/m', method=['GET'])
def cart_detail(request):
    """Cart detail view"""
    cart = Cart(request)
    logger.info(
        'Cart viewed by user %s (ID: %s)', 
        sanitize_input(request.user.username), 
        request.user.id
    )
    return render(request, 'cart/detail.html', {'cart': cart})

@login_required
@require_http_methods(["POST"])
@ratelimit(key='user', rate='10/m', method=['POST'])
def add_to_cart(request):
    """Add item to cart"""
    try:
        # Validate request origin
        validate_request_origin(request)
        
        # Sanitize and validate inputs
        controller_id = sanitize_input(request.POST.get('controller_id'))
        if not controller_id or not controller_id.isdigit():
            raise ValidationError("Invalid controller ID")
            
        quantity = validate_quantity(request.POST.get('quantity', 1))
        
        # Get controller and validate
        controller = get_object_or_404(Controller, id=controller_id)
        validate_controller(controller)
        
        # Get or create cart and validate limits
        cart, created = Cart.objects.get_or_create(user=request.user)
        validate_cart_limits(cart, quantity)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            controller=controller,
            defaults={'quantity': quantity}
        )
        
        if not created:
            new_quantity = validate_quantity(cart_item.quantity + quantity)
            validate_cart_limits(cart, new_quantity - cart_item.quantity)
            cart_item.quantity = new_quantity
            cart_item.save()
            
    except ValidationError as e:
        logger.warning(
            'Validation error for user %s (ID: %s): %s', 
            sanitize_input(request.user.username), 
            request.user.id,
            sanitize_input(str(e))
        )
    except Exception as e:
        logger.error(
            'Cart error for user %s (ID: %s): %s', 
            sanitize_input(request.user.username), 
            request.user.id,
            sanitize_input(str(e))
        )
        
    return redirect('cart:cart_detail')

@login_required
@require_http_methods(["POST"])
@never_cache
@ratelimit(key='user', rate='20/m', method=['POST'])
def update_cart(request):
    """Update cart item quantity"""
    try:
        # Sanitize and validate inputs
        item_id = sanitize_input(request.POST.get('item_id'))
        if not item_id or not item_id.isdigit():
            raise ValidationError("Invalid item ID")
            
        quantity = validate_quantity(request.POST.get('quantity', 0))
        
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            logger.info(
                'Cart item updated: user=%s (ID: %s), item=%s, quantity=%s', 
                sanitize_input(request.user.username), 
                request.user.id,
                item_id,
                quantity
            )
        else:
            cart_item.delete()
            logger.info(
                'Cart item removed: user=%s (ID: %s), item=%s', 
                sanitize_input(request.user.username), 
                request.user.id,
                item_id
            )
            
    except ValidationError as e:
        logger.warning(
            'Validation error for user %s (ID: %s): %s', 
            sanitize_input(request.user.username), 
            request.user.id,
            sanitize_input(str(e))
        )
    except Exception as e:
        logger.error(
            'Cart error for user %s (ID: %s): %s', 
            sanitize_input(request.user.username), 
            request.user.id,
            sanitize_input(str(e))
        )
        
    return redirect('cart:cart_detail')

@require_POST
def cart_add(request):
    cart = Cart(request)
    controller_id = request.POST.get('controller_id')
    controller = get_object_or_404(Controller, id=controller_id)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(controller=controller, quantity=quantity)
    return redirect('cart:cart_detail')

def cart_remove(request, controller_id):
    cart = Cart(request)
    controller = get_object_or_404(Controller, id=controller_id)
    cart.remove(controller)
    return redirect('cart:cart_detail') 