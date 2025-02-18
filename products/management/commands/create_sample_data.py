from django.core.management.base import BaseCommand
from django.core.files import File
from products.models import Category, Controller
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Creates sample data for the game controllers store'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')
        
        # First, clear existing data
        Controller.objects.all().delete()
        Category.objects.all().delete()
        
        # Create Category
        arcade_category = Category.objects.create(
            name='Arcade Controllers',
            slug='arcade-controllers',
            description='Professional arcade-style gaming controllers'
        )
        self.stdout.write(f'Created category: {arcade_category.name}')

        # Sample controllers data
        controllers_data = [
            {
                'name': 'Pro Fighter X8',
                'description': 'Tournament-grade arcade controller featuring premium Sanwa parts. Perfect for fighting games with its precise 8-way microswitch joystick and rapid-response buttons.',
                'price': 199.99,
                'featured': True,
                'image_name': 'controller1.jpg'
            },
            {
                'name': 'Classic Arcade Plus',
                'description': 'Customizable arcade controller with RGB LED buttons. Features programmable light patterns and authentic arcade feel.',
                'price': 249.99,
                'featured': True,
                'image_name': 'controller2.jpg'
            },
            {
                'name': 'Tournament Edition Pro',
                'description': 'Professional-grade controller with aluminum case and premium components. Built for competitive gaming.',
                'price': 299.99,
                'featured': True,
                'image_name': 'controller3.jpg'
            }
        ]

        # Create controllers
        for controller_data in controllers_data:
            image_name = controller_data.pop('image_name')
            controller, created = Controller.objects.get_or_create(
                name=controller_data['name'],
                defaults={
                    **controller_data,
                    'category': arcade_category
                }
            )

            if created and image_name:
                # Set the image if it exists
                image_path = os.path.join(settings.BASE_DIR, 'static', 'images', image_name)
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as image_file:
                        controller.image.save(image_name, File(image_file), save=True)
                    self.stdout.write(f'Added image {image_name} to {controller.name}')
                else:
                    self.stdout.write(self.style.WARNING(f'Image not found: {image_path}'))

            status = 'Created' if created else 'Found'
            self.stdout.write(f'{status} controller: {controller.name}')

        self.stdout.write(self.style.SUCCESS('Sample data created successfully')) 