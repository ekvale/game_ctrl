from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from products.models import Controller, Category
from decimal import Decimal
from django.utils.text import slugify
import random

class Command(BaseCommand):
    help = 'Generates sample data for the game_ctrl application'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')

        # Create categories
        categories = [
            'PlayStation',
            'Xbox',
            'Nintendo',
            'PC',
            'Retro',
        ]

        for cat_name in categories:
            Category.objects.get_or_create(
                name=cat_name,
                defaults={
                    'slug': slugify(cat_name)
                }
            )

        # Create sample controllers
        sample_controllers = [
            {
                'name': 'DualSense Wireless Controller',
                'category_name': 'PlayStation',
                'price': Decimal('69.99'),
                'description': 'Next-gen PlayStation 5 controller with haptic feedback.',
                'is_featured': True,
            },
            {
                'name': 'Xbox Elite Controller Series 2',
                'category_name': 'Xbox',
                'price': Decimal('179.99'),
                'description': 'Premium Xbox controller with customizable components.',
                'is_featured': True,
            },
            {
                'name': 'Nintendo Switch Pro Controller',
                'category_name': 'Nintendo',
                'price': Decimal('69.99'),
                'description': 'Professional controller for Nintendo Switch.',
                'is_featured': False,
            },
        ]

        for controller_data in sample_controllers:
            category = Category.objects.get(name=controller_data['category_name'])
            Controller.objects.get_or_create(
                name=controller_data['name'],
                defaults={
                    'category': category,
                    'price': controller_data['price'],
                    'description': controller_data['description'],
                    'is_featured': controller_data['is_featured'],
                    'slug': slugify(controller_data['name']),
                    'available': True,
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully created sample data')) 