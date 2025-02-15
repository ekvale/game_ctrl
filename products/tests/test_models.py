import pytest
from django.urls import reverse
from products.models import Category, Controller
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError

@pytest.mark.django_db
class TestCategoryModel:
    def test_category_creation(self):
        category = Category.objects.create(
            name="PlayStation",
            slug="playstation"
        )
        assert category.name == "PlayStation"
        assert category.slug == "playstation"
        assert str(category) == "PlayStation"
        
    def test_category_unique_slug(self):
        Category.objects.create(name="PlayStation", slug="playstation")
        with pytest.raises(Exception):
            Category.objects.create(name="PlayStation 2", slug="playstation")
    
    def test_get_absolute_url(self):
        category = Category.objects.create(
            name="Nintendo",
            slug="nintendo"
        )
        assert category.get_absolute_url() == reverse('products:category_detail', args=['nintendo'])

@pytest.mark.django_db
class TestControllerModel:
    @pytest.fixture
    def category(self):
        return Category.objects.create(
            name="PlayStation",
            slug="playstation"
        )
    
    @pytest.fixture
    def image_file(self):
        return SimpleUploadedFile(
            name='test_image.jpg',
            content=b'',  # empty image
            content_type='image/jpeg'
        )
    
    def test_controller_creation(self, category, image_file):
        controller = Controller.objects.create(
            category=category,
            name="PS5 Custom Controller",
            slug="ps5-custom-controller",
            image=image_file,
            description="A custom PS5 controller",
            price=99.99,
            available=True
        )
        assert controller.name == "PS5 Custom Controller"
        assert controller.price == 99.99
        assert controller.available == True
        assert str(controller) == "PS5 Custom Controller"
        
    def test_controller_unavailable(self, category):
        controller = Controller.objects.create(
            category=category,
            name="Out of Stock Controller",
            slug="out-of-stock",
            price=149.99,
            available=False
        )
        assert not controller.available
        
    def test_get_absolute_url(self, category):
        controller = Controller.objects.create(
            category=category,
            name="Test Controller",
            slug="test-controller",
            price=99.99
        )
        assert controller.get_absolute_url() == reverse('products:controller_detail', args=['test-controller'])

    def test_controller_ordering(self, category):
        """Test that controllers are ordered correctly by name"""
        Controller.objects.create(
            category=category,
            name="Xbox Controller",
            slug="xbox",
            price=199.99
        )
        Controller.objects.create(
            category=category,
            name="PlayStation Controller",
            slug="ps",
            price=189.99
        )
        
        controllers = Controller.objects.all()
        assert controllers[0].name == "PlayStation Controller"
        assert controllers[1].name == "Xbox Controller"

    def test_category_str_representation(self):
        """Test the string representation of Category"""
        category = Category.objects.create(
            name="Test Category",
            slug="test-category"
        )
        assert str(category) == "Test Category"

    def test_controller_price_validation(self, category):
        """Test price validation on Controller model"""
        with pytest.raises(ValidationError):
            controller = Controller(
                category=category,
                name="Invalid Price Controller",
                slug="invalid-price",
                price=-10.00
            )
            controller.full_clean() 