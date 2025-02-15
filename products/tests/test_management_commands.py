import pytest
from django.core.management import call_command
from django.core.files.storage import default_storage
from products.models import Category, Controller
from io import StringIO
from decimal import Decimal
from django.test import TestCase
from django.core.management.base import CommandError
from unittest.mock import patch
import os

@pytest.mark.django_db
class TestCreateSampleData(TestCase):
    def test_create_sample_data_command(self):
        """Test create_sample_data command creates expected objects"""
        # Execute command
        call_command('create_sample_data')
        
        # Verify categories were created
        self.assertTrue(Category.objects.exists())
        self.assertGreater(Category.objects.count(), 0)
        
        # Verify controllers were created
        self.assertTrue(Controller.objects.exists())
        self.assertGreater(Controller.objects.count(), 0)

    def test_controller_prices(self):
        """Test created controllers have valid prices"""
        # Execute command
        call_command('create_sample_data')
        
        # Verify all controllers have valid prices
        for controller in Controller.objects.all():
            self.assertGreater(controller.price, Decimal('0'))
            self.assertLess(controller.price, Decimal('1000'))

    def test_category_relationships(self):
        """Test controllers are properly assigned to categories"""
        # Execute command
        call_command('create_sample_data')
        
        # Verify each controller has a category
        for controller in Controller.objects.all():
            self.assertIsNotNone(controller.category)
            self.assertTrue(isinstance(controller.category, Category))

    @patch('products.management.commands.create_sample_data.Category.objects.get_or_create')
    def test_database_error_handling(self, mock_create):
        """Test command handles database errors"""
        # Setup
        mock_create.side_effect = Exception("Database error")
        
        # Verify
        with self.assertRaises(CommandError):
            call_command('create_sample_data')

    def test_idempotency(self):
        """Test running command multiple times doesn't duplicate data"""
        # Execute command twice
        call_command('create_sample_data')
        initial_category_count = Category.objects.count()
        initial_controller_count = Controller.objects.count()
        
        call_command('create_sample_data')
        
        # Verify counts haven't changed
        self.assertEqual(Category.objects.count(), initial_category_count)
        self.assertEqual(Controller.objects.count(), initial_controller_count)

    @patch('os.path.exists')
    def test_create_sample_data_command_output(self, mock_exists):
        # Setup
        mock_exists.return_value = True  # Pretend image files exist
        
        # Call the command
        out = StringIO()
        call_command('create_sample_data', stdout=out)
        
        # Check output
        output = out.getvalue()
        assert 'Creating sample data...' in output
        assert 'Created category: Arcade Controllers' in output
        assert 'Sample data created successfully' in output
        
        # Check database
        assert Category.objects.count() == 1
        assert Controller.objects.count() == 3
        
        # Check specific controllers
        controllers = Controller.objects.all()
        controller_names = set(c.name for c in controllers)
        assert {'Pro Fighter X8', 'Classic Arcade Plus', 'Tournament Edition Pro'} == controller_names

    def test_controller_prices_command(self):
        call_command('create_sample_data')
        
        pro_fighter = Controller.objects.get(slug='pro-fighter-x8')
        classic = Controller.objects.get(slug='classic-arcade-plus')
        tournament = Controller.objects.get(slug='tournament-edition-pro')
        
        assert pro_fighter.price == Decimal('199.99')
        assert classic.price == Decimal('149.99')
        assert tournament.price == Decimal('249.99') 