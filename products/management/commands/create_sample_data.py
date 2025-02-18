from django.core.management.base import BaseCommand
from django.core.files import File
from products.models import Category, Controller
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Creates sample data for the game controllers store'

    def handle(self, *args, **kwargs):
        # Create Category
        arcade_category, created = Category.objects.get_or_create(
            name='Arcade Controllers',
            slug='arcade-controllers',
            description='Professional arcade-style gaming controllers'
        )

        # Sample controllers data
        controllers_data = [
            {
                'name': 'Pro Fighter X',
                'description': 'Tournament-grade arcade controller featuring Sanwa buttons and joystick. Perfect for fighting games with its precise 8-way microswitch joystick and rapid-response buttons.',
                'price': 199.99,
                'featured': True,
                'image_name': 'controller1.jpg'
            },
            {
                'name': 'Custom LED Master',
                'description': 'Customizable arcade controller with RGB LED buttons. Features programmable light patterns and premium Japanese arcade parts.',
                'price': 249.99,
                'featured': True,
                'image_name': None
            },
            {
                'name': 'Retro Classic',
                'description': 'Classic-styled arcade controller with authentic feel. Perfect for retro gaming and modern classics.',
                'price': 159.99,
                'featured': True,
                'image_name': None
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
                image_path = os.path.join(settings.STATIC_ROOT, 'images', image_name)
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as image_file:
                        controller.image.save(image_name, File(image_file), save=True)

            status = 'Created' if created else 'Already exists'
            self.stdout.write(self.style.SUCCESS(f'{status}: {controller.name}')) 