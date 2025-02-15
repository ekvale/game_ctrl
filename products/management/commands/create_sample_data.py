from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from products.models import Category, Controller
from pathlib import Path
import os
from decimal import Decimal

class Command(BaseCommand):
    help = 'Create sample data for development'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        try:
            # Create or get category
            arcade, created = Category.objects.get_or_create(
                name='Arcade Controllers',
                slug='arcade-controllers'
            )
            if created:
                self.stdout.write(f'Created category: {arcade.name}')
            else:
                self.stdout.write(f'Using existing category: {arcade.name}')

            # Create or update controllers
            controllers_data = [
                {
                    'name': 'Pro Fighter X8',
                    'slug': 'pro-fighter-x8',
                    'price': Decimal('199.99'),
                    'description': 'Professional grade arcade controller',
                    'image_name': 'pro-fighter-x8.svg'
                },
                {
                    'name': 'Classic Arcade Plus',
                    'slug': 'classic-arcade-plus',
                    'price': Decimal('149.99'),
                    'description': 'Classic style arcade controller',
                    'image_name': 'classic-arcade-plus.svg'
                },
                {
                    'name': 'Tournament Edition Pro',
                    'slug': 'tournament-edition-pro',
                    'price': Decimal('249.99'),
                    'description': 'Tournament ready arcade controller',
                    'image_name': 'tournament-edition-pro.svg'
                }
            ]

            for data in controllers_data:
                try:
                    # Try to get existing controller
                    controller = Controller.objects.get(slug=data['slug'])
                    self.stdout.write(f'Using existing controller: {controller.name}')
                except Controller.DoesNotExist:
                    # Create new controller
                    try:
                        image_path = f"static/images/{data['image_name']}"
                        if os.path.exists(image_path):
                            with open(image_path, 'rb') as f:
                                controller = Controller.objects.create(
                                    name=data['name'],
                                    slug=data['slug'],
                                    category=arcade,
                                    price=data['price'],
                                    description=data['description'],
                                    image=File(f, name=data['image_name'])
                                )
                        else:
                            controller = Controller.objects.create(
                                name=data['name'],
                                slug=data['slug'],
                                category=arcade,
                                price=data['price'],
                                description=data['description']
                            )
                        self.stdout.write(f'Created controller: {controller.name}')
                    except Exception as e:
                        raise CommandError(f'Failed to create controller {data["name"]}: {str(e)}')

            self.stdout.write(self.style.SUCCESS('Sample data created successfully'))
            
        except Exception as e:
            raise CommandError(f'Failed to create sample data: {str(e)}') 