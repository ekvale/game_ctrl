from django.core.management.base import BaseCommand
from products.models import Controller
from django.core.files import File
from pathlib import Path
import os

class Command(BaseCommand):
    help = 'Load product images for controllers'

    def handle(self, *args, **options):
        base_path = Path(__file__).resolve().parent.parent.parent.parent / 'static' / 'images' / 'products'
        base_path.mkdir(exist_ok=True)

        controllers = {
            'pro-fighter-x8': 'pro-fighter.jpg',
            'classic-arcade-plus': 'classic-arcade.jpg',
            'tournament-edition-pro': 'tournament-pro.jpg'
        }

        for slug, image_name in controllers.items():
            try:
                controller = Controller.objects.get(slug=slug)
                image_path = base_path / image_name
                if image_path.exists():
                    with open(image_path, 'rb') as f:
                        controller.image.save(image_name, File(f), save=True)
                    self.stdout.write(self.style.SUCCESS(f'Added image for {slug}'))
            except Controller.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Controller {slug} not found')) 