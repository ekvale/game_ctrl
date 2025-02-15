import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from products.models import Category, Controller
from cart.models import Cart, CartItem
from decimal import Decimal

@pytest.mark.django_db
class TestCartViews:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = Client()
        
        # Create test user
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create test category and controller
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.controller = Controller.objects.create(
            name='Test Controller',
            slug='test-controller',
            category=self.category,
            price=Decimal('199.99')
        )

    def test_cart_detail_requires_login(self):
        """Test that cart detail view requires login"""
        response = self.client.get(reverse('cart:cart_detail'))
        assert response.status_code == 302
        assert '/login/' in response.url

    def test_cart_detail_view(self):
        """Test the cart detail view with items"""
        # Login
        self.client.login(username='testuser', password='testpass123')
        
        # Create cart and add item
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(
            cart=cart,
            controller=self.controller,
            quantity=2
        )
        
        response = self.client.get(reverse('cart:cart_detail'))
        
        assert response.status_code == 200
        assert 'cart/cart_detail.html' in [t.name for t in response.templates]
        assert response.context['cart'] == cart
        assert list(response.context['cart_items']) == [cart_item]
        assert b'Test Controller' in response.content
        assert b'Quantity: 2' in response.content

    def test_cart_detail_empty_cart(self):
        """Test cart detail view with empty cart"""
        # Login
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('cart:cart_detail'))
        
        assert response.status_code == 200
        assert 'cart/cart_detail.html' in [t.name for t in response.templates]
        assert response.context['cart'].items.count() == 0
        assert b'Your cart is empty' in response.content

    def test_cart_detail_creates_cart(self):
        """Test that cart detail view creates a cart if none exists"""
        # Login
        self.client.login(username='testuser', password='testpass123')
        
        # Verify no cart exists
        assert not Cart.objects.filter(user=self.user).exists()
        
        response = self.client.get(reverse('cart:cart_detail'))
        
        assert response.status_code == 200
        assert Cart.objects.filter(user=self.user).exists()

    def test_add_to_cart_requires_login(self):
        """Test that add_to_cart view requires login"""
        response = self.client.post(reverse('cart:add_to_cart'), {
            'controller_id': self.controller.id,
            'quantity': 1
        })
        assert response.status_code == 302
        assert '/login/' in response.url

    def test_add_to_cart_get_request(self):
        """Test that GET requests to add_to_cart are ignored"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('cart:add_to_cart'))
        
        assert response.status_code == 302
        assert not Cart.objects.filter(user=self.user).exists()

    def test_add_to_cart_invalid_controller(self):
        """Test adding non-existent controller to cart"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('cart:add_to_cart'), {
            'controller_id': 999,  # Non-existent ID
            'quantity': 1
        })
        
        assert response.status_code == 404

    def test_add_to_cart_increment_quantity(self):
        """Test adding same controller multiple times increments quantity"""
        self.client.login(username='testuser', password='testpass123')
        
        # Add controller first time
        self.client.post(reverse('cart:add_to_cart'), {
            'controller_id': self.controller.id,
            'quantity': 1
        })
        
        # Add same controller second time
        self.client.post(reverse('cart:add_to_cart'), {
            'controller_id': self.controller.id,
            'quantity': 2
        })
        
        cart = Cart.objects.get(user=self.user)
        cart_item = cart.items.first()
        assert cart_item.quantity == 3  # 1 + 2

    def test_update_cart_requires_login(self):
        """Test that update_cart view requires login"""
        response = self.client.post(reverse('cart:update_cart'), {
            'item_id': 1,
            'quantity': 1
        })
        assert response.status_code == 302
        assert '/login/' in response.url

    def test_update_cart_missing_item_id(self):
        """Test update_cart with missing item_id"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('cart:update_cart'), {
            'quantity': 1
        })
        
        assert response.status_code == 404

    def test_update_cart_invalid_quantity_format(self):
        """Test update_cart with invalid quantity format"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create cart and item
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(
            cart=cart,
            controller=self.controller,
            quantity=1
        )
        
        # Try to update with invalid quantity
        response = self.client.post(reverse('cart:update_cart'), {
            'item_id': cart_item.id,
            'quantity': 'invalid'
        })
        
        assert response.status_code == 302
        cart_item.refresh_from_db()
        assert cart_item.quantity == 1  # Quantity should not change

    def test_update_cart(self):
        """Test updating cart item quantity"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create cart and add item
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(
            cart=cart,
            controller=self.controller,
            quantity=1
        )
        
        # Update quantity
        response = self.client.post(reverse('cart:update_cart'), {
            'item_id': cart_item.id,
            'quantity': 3
        })
        
        assert response.status_code == 302
        cart_item.refresh_from_db()
        assert cart_item.quantity == 3

    def test_update_cart_invalid_item(self):
        """Test updating cart with invalid item id"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('cart:update_cart'), {
            'item_id': 999,  # Non-existent ID
            'quantity': 3
        })
        
        assert response.status_code == 404

    def test_update_cart_wrong_user(self):
        """Test updating cart item belonging to another user"""
        # Create another user and their cart
        other_user = get_user_model().objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        other_cart = Cart.objects.create(user=other_user)
        other_item = CartItem.objects.create(
            cart=other_cart,
            controller=self.controller,
            quantity=1
        )
        
        # Login as original user and try to update other user's item
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('cart:update_cart'), {
            'item_id': other_item.id,
            'quantity': 3
        })
        
        assert response.status_code == 404
        other_item.refresh_from_db()
        assert other_item.quantity == 1  # Quantity should not change

    def test_remove_from_cart(self):
        """Test removing items from cart"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create cart and add item
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(
            cart=cart,
            controller=self.controller,
            quantity=1
        )
        
        # Remove item by setting quantity to 0
        response = self.client.post(reverse('cart:update_cart'), {
            'item_id': cart_item.id,
            'quantity': 0
        })
        
        assert response.status_code == 302
        assert not CartItem.objects.filter(id=cart_item.id).exists()

    def test_cart_detail_multiple_items(self):
        """Test cart detail view with multiple items"""
        # Login
        self.client.login(username='testuser', password='testpass123')

        # Create cart
        cart = Cart.objects.create(user=self.user)

        # Add first item
        CartItem.objects.create(
            cart=cart,
            controller=self.controller,
            quantity=2
        )

        # Create and add second controller
        controller2 = Controller.objects.create(
            name='Test Controller 2',
            slug='test-controller-2',
            category=self.category,
            price=Decimal('299.99')
        )
        CartItem.objects.create(
            cart=cart,
            controller=controller2,
            quantity=1
        )

        response = self.client.get(reverse('cart:cart_detail'))
        
        assert response.status_code == 200
        assert response.context['cart_items'].count() == 2
        assert b'Test Controller' in response.content
        assert b'Test Controller 2' in response.content
        assert b'Quantity: 2' in response.content
        assert b'Quantity: 1' in response.content

    def test_update_cart_get_request(self):
        """Test that GET requests to update_cart are ignored"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create cart and item
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(
            cart=cart,
            controller=self.controller,
            quantity=1
        )
        
        # Try GET request
        response = self.client.get(reverse('cart:update_cart'))
        
        assert response.status_code == 302  # Should redirect
        cart_item.refresh_from_db()
        assert cart_item.quantity == 1  # Quantity should not change

    def test_update_cart_missing_params(self):
        """Test update_cart with missing parameters"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create cart and item
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(
            cart=cart,
            controller=self.controller,
            quantity=1
        )
        
        # Post without quantity
        response = self.client.post(reverse('cart:update_cart'), {
            'item_id': cart_item.id
        })
        
        assert response.status_code == 302
        # Item should be deleted since quantity defaults to 0
        assert not CartItem.objects.filter(id=cart_item.id).exists() 