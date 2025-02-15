import pytest
from django.contrib.admin.sites import AdminSite
from django.utils import timezone
from datetime import timedelta
from products.admin import MonitoringAdmin, ControllerAdmin
from products.models import Controller, Category
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from unittest.mock import patch
from decimal import Decimal

@pytest.mark.django_db
class TestMonitoringAdmin:
    @pytest.fixture
    def admin_site(self):
        return AdminSite()
    
    @pytest.fixture
    def monitoring_admin(self, admin_site):
        return MonitoringAdmin(Controller, admin_site)
    
    @pytest.fixture
    def admin_user(self):
        User = get_user_model()
        return User.objects.create_superuser('admin', 'admin@test.com', 'password')
    
    @pytest.fixture
    def category(self):
        return Category.objects.create(name="Test Category", slug="test-category")
    
    def test_changelist_view_stats(self, monitoring_admin, admin_user, rf, category):
        # Create a fixed time for testing
        fixed_time = timezone.now()
        
        # Create controllers at different times
        recent = Controller.objects.create(
            category=category,
            name="Recent Controller",
            slug="recent-controller",
            price=199.99,
            available=True
        )
        # Manually update created_at
        Controller.objects.filter(pk=recent.pk).update(created_at=fixed_time)
        
        old = Controller.objects.create(
            category=category,
            name="Old Controller",
            slug="old-controller",
            price=149.99,
            available=True
        )
        # Manually update created_at
        Controller.objects.filter(pk=old.pk).update(
            created_at=fixed_time - timedelta(days=2)
        )

        # Create request
        request = rf.get('/admin/products/controller/')
        request.user = admin_user
        
        # Mock timezone.now() just for the view execution
        with patch('django.utils.timezone.now', return_value=fixed_time):
            response = monitoring_admin.changelist_view(request)
        
        # Check context data
        assert 'summary' in response.context_data
        summary = response.context_data['summary']
        assert summary['total'] == 2
        assert summary['last_24h'] == 1
        assert summary['revenue_24h'] == Decimal('199.99')

    def test_controller_admin_configuration(self, admin_site):
        admin = ControllerAdmin(Controller, admin_site)
        assert 'name' in admin.list_display
        assert 'price' in admin.list_editable
        assert 'available' in admin.list_filter
        assert 'name' in admin.search_fields 

    def test_admin_list_filters(self, admin_site, category, admin_user):
        """Test that admin list filters work correctly"""
        admin = ControllerAdmin(Controller, admin_site)
        
        # Create controllers with different states
        Controller.objects.create(
            category=category,
            name="Available Controller",
            slug="available",
            price=199.99,
            available=True
        )
        Controller.objects.create(
            category=category,
            name="Unavailable Controller",
            slug="unavailable",
            price=149.99,
            available=False
        )
        
        # Test available filter
        request = RequestFactory().get('/')
        request.user = admin_user
        changelist = admin.get_changelist_instance(request)
        filtered = changelist.get_queryset(request).filter(available=True)
        assert filtered.count() == 1
        assert filtered.first().name == "Available Controller"

    def test_admin_search(self, admin_site, category, admin_user):
        """Test that admin search functionality works"""
        admin = ControllerAdmin(Controller, admin_site)
        
        # Create test controllers
        Controller.objects.create(
            category=category,
            name="PlayStation Controller",
            slug="ps-controller",
            price=199.99,
            description="Official PlayStation controller"
        )
        Controller.objects.create(
            category=category,
            name="Xbox Controller",
            slug="xbox-controller",
            price=189.99,
            description="Gaming controller"
        )
        
        # Test search by name
        request = RequestFactory().get('/', {'q': 'PlayStation'})
        request.user = admin_user
        changelist = admin.get_changelist_instance(request)
        filtered = changelist.get_queryset(request)
        assert filtered.count() == 1
        assert filtered.first().name == "PlayStation Controller" 