import pytest
from django.template.loader import render_to_string
from django.template import Template, Context
from django.urls import reverse
from django.contrib.auth.models import User
from products.models import Category, Controller

@pytest.mark.django_db
class TestTemplates:
    @pytest.fixture
    def category(self):
        return Category.objects.create(
            name="Test Category",
            slug="test-category"
        )
    
    @pytest.fixture
    def controller(self, category):
        return Controller.objects.create(
            category=category,
            name="Test Controller",
            slug="test-controller",
            price=99.99,
            available=True
        )

    def test_home_template_sections(self):
        context = {
            'featured_controllers': [],
            'categories': []
        }
        rendered = render_to_string('products/home.html', context)
        
        # Test all major sections are present
        assert 'hero-section' in rendered
        assert 'features py-5' in rendered
        assert 'video-section py-5' in rendered
        assert 'custom-builds' in rendered
        assert 'cta-section' in rendered
        
        # Test video section elements
        assert 'See How It Works' in rendered
        assert 'Professional-grade components' in rendered
        assert 'ratio ratio-16x9' in rendered
    
    def test_product_card_structure(self):
        template_content = '''
        <div class="product-card card h-100">
            {% if controller.image %}
            <img src="{{ controller.image.url }}" class="card-img-top" alt="{{ controller.name }}">
            {% endif %}
            <div class="card-body">
                <h5 class="card-title">{{ controller.name }}</h5>
                <p class="card-text">{{ controller.description }}</p>
                <div class="d-flex justify-content-between align-items-center">
                    <span class="h5 mb-0">${{ controller.price }}</span>
                    <a href="{{ controller.get_absolute_url }}" class="btn btn-primary">View Details</a>
                </div>
            </div>
        </div>
        '''
        
        context = {
            'controller': {
                'name': 'Test Controller',
                'image': {'url': '/test.svg'},
                'description': 'Test description',
                'price': '99.99',
                'get_absolute_url': '/test/'
            }
        }
        
        template = Template(template_content)
        rendered = template.render(Context(context))
        
        # Test card structure
        assert 'product-card' in rendered
        assert 'card-img-top' in rendered
        assert 'card-body' in rendered
        assert 'btn-primary' in rendered
        
        # Test content
        assert 'Test Controller' in rendered
        assert '/test.svg' in rendered
        assert 'Test description' in rendered
        assert '99.99' in rendered
        assert '/test/' in rendered

    def test_controller_price_formatting(self, client, controller):
        """Test that controller prices are properly formatted in templates"""
        url = reverse('products:controller_detail', args=[controller.slug])
        response = client.get(url, secure=True)
        content = response.content.decode('utf-8')
        
        # Price should be formatted with 2 decimal places
        assert f"${controller.price:.2f}" in content

    @pytest.mark.django_db
    def test_category_list_empty_message(self, client):
        """Test that appropriate message is shown when category has no controllers"""
        category = Category.objects.create(name="Empty Category", slug="empty")
        url = reverse('products:category_detail', args=[category.slug])
        response = client.get(url, secure=True)
        content = response.content.decode('utf-8')
        
        # Verify category name is shown
        assert category.name in content
        # Verify empty message is shown
        assert '<div class="alert alert-info">' in content
        assert 'No controllers available in this category' in content
        # Verify there are no product cards
        assert 'product-card' not in content 