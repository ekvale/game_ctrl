import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from products.models import Category, Controller
from cart.models import Cart, CartItem

@pytest.mark.django_db
class TestCartModel:
    @pytest.fixture(autouse=True)
    def setup(self):
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

    def test_cart_creation(self):
        """Test creating a cart"""
        cart = Cart.objects.create(user=self.user)
        assert cart.user == self.user
        assert cart.items.count() == 0
        assert cart.total_price == Decimal('0')

    def test_cart_str(self):
        """Test cart string representation"""
        cart = Cart.objects.create(user=self.user)
        assert str(cart) == f"Cart for {self.user.username}"

    def test_cart_total_price(self):
        """Test cart total price calculation"""
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
        
        # Total should be (199.99 * 2) + (299.99 * 1) = 699.97
        assert cart.total_price == Decimal('699.97')

    def test_cart_str_method(self):
        """Test Cart string representation includes username"""
        cart = Cart.objects.create(user=self.user)
        assert str(cart) == f"Cart for {self.user.username}"

    def test_cart_total_price_empty_cart(self):
        """Test cart total price with empty cart"""
        cart = Cart.objects.create(user=self.user)
        assert cart.total_price == Decimal('0')

    def test_cart_total_price_multiple_items(self):
        """Test cart total price with multiple items"""
        cart = Cart.objects.create(user=self.user)
        
        # First item: 199.99 * 2 = 399.98
        CartItem.objects.create(
            cart=cart,
            controller=self.controller,
            quantity=2
        )
        
        # Second item: 299.99 * 3 = 899.97
        controller2 = Controller.objects.create(
            name='Test Controller 2',
            slug='test-controller-2',
            category=self.category,
            price=Decimal('299.99')
        )
        CartItem.objects.create(
            cart=cart,
            controller=controller2,
            quantity=3
        )
        
        # Total should be 399.98 + 899.97 = 1299.95
        assert cart.total_price == Decimal('1299.95')

@pytest.mark.django_db
class TestCartItemModel:
    @pytest.fixture(autouse=True)
    def setup(self):
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
        
        # Create cart
        self.cart = Cart.objects.create(user=self.user)

    def test_cart_item_creation(self):
        """Test creating a cart item"""
        cart_item = CartItem.objects.create(
            cart=self.cart,
            controller=self.controller,
            quantity=2
        )
        
        assert cart_item.cart == self.cart
        assert cart_item.controller == self.controller
        assert cart_item.quantity == 2
        assert cart_item.total_price == Decimal('399.98')  # 199.99 * 2

    def test_cart_item_str(self):
        """Test cart item string representation"""
        cart_item = CartItem.objects.create(
            cart=self.cart,
            controller=self.controller,
            quantity=2
        )
        assert str(cart_item) == f"{cart_item.quantity}x {self.controller.name}"

    def test_cart_item_update_quantity(self):
        """Test updating cart item quantity"""
        cart_item = CartItem.objects.create(
            cart=self.cart,
            controller=self.controller,
            quantity=1
        )
        
        cart_item.quantity = 3
        cart_item.save()
        
        assert cart_item.quantity == 3
        assert cart_item.total_price == Decimal('599.97')  # 199.99 * 3

    def test_cart_item_quantity_validation(self):
        with pytest.raises(Exception):
            CartItem.objects.create(
                cart=self.cart,
                controller=self.controller,
                quantity=-1
            )
            
    def test_cart_multiple_items(self):
        CartItem.objects.create(
            cart=self.cart,
            controller=self.controller,
            quantity=2
        )
        
        controller2 = Controller.objects.create(
            category=self.category,
            name="Xbox Controller",
            slug="xbox-controller",
            price=89.99
        )
        
        CartItem.objects.create(
            cart=self.cart,
            controller=controller2,
            quantity=1
        )
        
        assert self.cart.items.count() == 2

    def test_cart_item_total_price_calculation(self):
        """Test CartItem total_price property calculates correctly"""
        cart_item = CartItem.objects.create(
            cart=self.cart,
            controller=self.controller,
            quantity=3
        )
        # 199.99 * 3 = 599.97
        assert cart_item.total_price == Decimal('599.97')

    def test_cart_item_total_price_zero_quantity(self):
        """Test cart item total price with zero quantity"""
        cart_item = CartItem.objects.create(
            cart=self.cart,
            controller=self.controller,
            quantity=0
        )
        assert cart_item.total_price == Decimal('0') 