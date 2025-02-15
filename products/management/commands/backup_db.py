from django.core.management.base import BaseCommand, CommandError
from django.core import serializers
from products.models import Category, Controller
from cart.models import Cart, CartItem
import os
from datetime import datetime

class Command(BaseCommand):
    help = 'Backup database to JSON file'

    def handle(self, *args, **options):
        # Create backups directory if it doesn't exist
        if not os.path.exists('backups'):
            os.makedirs('backups')

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f'backup_{timestamp}.json'
        filepath = os.path.join('backups', filename)

        try:
            # Get all models to backup
            models_to_backup = [
                Category.objects.all(),
                Controller.objects.all(),
                Cart.objects.all(),
                CartItem.objects.all(),
            ]

            # Serialize data
            data = serializers.serialize('json', [
                obj for queryset in models_to_backup
                for obj in queryset
            ])

            # Write to file
            with open(filepath, 'w') as f:
                f.write(data)

            self.stdout.write(
                self.style.SUCCESS(f'Successfully created backup: {filename}')
            )
        except Exception as e:
            raise CommandError(f'Backup failed: {str(e)}') 