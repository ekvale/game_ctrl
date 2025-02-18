from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from products.models import Product, Category
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Generates sample data for the game_ctrl application'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')

        # Create categories
        categories = [
            'Action Games',
            'RPG Games',
            'Strategy Games',
            'Sports Games',
            'Adventure Games',
        ]

        for cat_name in categories:
            Category.objects.get_or_create(name=cat_name)

        # Create sample products
        sample_products = [
            {
                'name': 'The Elder Scrolls V: Skyrim',
                'category': 'RPG Games',
                'price': Decimal('29.99'),
                'description': 'Epic fantasy RPG with dragons and magic.',
            },
            {
                'name': 'FIFA 24',
                'category': 'Sports Games',
                'price': Decimal('59.99'),
                'description': 'Latest football simulation game.',
            },
            {
                'name': 'Red Dead Redemption 2',
                'category': 'Action Games',
                'price': Decimal('49.99'),
                'description': 'Wild West action-adventure game.',
            },
            # Add more products as needed
        ]

        for product_data in sample_products:
            category = Category.objects.get(name=product_data['category'])
            Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'category': category,
                    'price': product_data['price'],
                    'description': product_data['description'],
                    'stock': random.randint(10, 100),
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully created sample data')) 