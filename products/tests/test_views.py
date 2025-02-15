import pytest
from django.test import Client
from django.urls import reverse
from products.models import Category, Controller
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import timedelta

@pytest.mark.django_db
class TestProductViews:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = Client()
        
        # Create test category
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        
        # Create test controllers
        self.controller = Controller.objects.create(
            name='Test Controller',
            slug='test-controller',
            category=self.category,
            price=Decimal('199.99'),
            is_featured=True
        )
        
        # Create some non-featured controllers
        for i in range(7):  # Create 7 more controllers (8 total)
            Controller.objects.create(
                name=f'Controller {i}',
                slug=f'controller-{i}',
                category=self.category,
                price=Decimal('99.99'),
                is_featured=True
            )

    def test_home_view(self):
        """Test home page view"""
        response = self.client.get(reverse('products:home'))
        
        assert response.status_code == 200
        assert 'products/home.html' in [t.name for t in response.templates]
        assert 'categories' in response.context
        assert 'featured_controllers' in response.context
        assert list(response.context['categories']) == [self.category]
        assert len(response.context['featured_controllers']) == 6  # Test limit

    def test_category_detail(self):
        """Test category detail view"""
        response = self.client.get(
            reverse('products:category_detail', kwargs={'slug': self.category.slug})
        )
        
        assert response.status_code == 200
        assert 'products/category_detail.html' in [t.name for t in response.templates]
        assert response.context['category'] == self.category
        assert self.controller in response.context['controllers']

    def test_controller_detail(self):
        """Test controller detail view"""
        response = self.client.get(
            reverse('products:controller_detail', kwargs={'slug': self.controller.slug})
        )
        
        assert response.status_code == 200
        assert 'products/controller_detail.html' in [t.name for t in response.templates]
        assert response.context['controller'] == self.controller

    def test_category_404(self):
        """Test category detail with invalid slug"""
        response = self.client.get(
            reverse('products:category_detail', kwargs={'slug': 'invalid-slug'})
        )
        assert response.status_code == 404

    def test_controller_404(self):
        """Test controller detail with invalid slug"""
        response = self.client.get(
            reverse('products:controller_detail', kwargs={'slug': 'invalid-slug'})
        )
        assert response.status_code == 404

    def test_featured_controllers_limit(self):
        """Test that home page limits featured controllers to 6"""
        response = self.client.get(reverse('products:home'))
        featured = response.context['featured_controllers']
        assert len(featured) == 6
        assert all(c.is_featured for c in featured)

    def test_category_ordering(self):
        """Test that controllers in category are ordered by created_at"""
        # Create another controller that should appear first
        newer_controller = Controller.objects.create(
            name='Newer Controller',
            slug='newer-controller',
            category=self.category,
            price=Decimal('299.99')
        )
        newer_controller.created_at = timezone.now() + timedelta(days=1)
        newer_controller.save()
        
        response = self.client.get(
            reverse('products:category_detail', kwargs={'slug': self.category.slug})
        )
        
        controllers = response.context['controllers']
        assert controllers[0] == newer_controller  # Should be first due to ordering 