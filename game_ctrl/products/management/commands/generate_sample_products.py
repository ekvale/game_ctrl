from django.core.management.base import BaseCommand
from django.utils.text import slugify
from products.models import Controller
import random

class Command(BaseCommand):
    help = 'Generates sample controller products'

    def handle(self, *args, **kwargs):
        # Sample data for controllers
        controllers = [
            {
                'name': 'Pro Gaming Controller X',
                'description': 'Professional-grade gaming controller with customizable buttons and RGB lighting.',
                'price': 149.99,
                'is_featured': True,
            },
            {
                'name': 'Elite Performance Pad',
                'description': 'High-performance gaming pad with mechanical switches and premium build quality.',
                'price': 199.99,
                'is_featured': True,
            },
            {
                'name': 'Budget Gamer Pro',
                'description': 'Affordable gaming controller with all essential features.',
                'price': 49.99,
                'is_featured': False,
            },
            {
                'name': 'Wireless Gaming Master',
                'description': 'Low-latency wireless controller with extended battery life.',
                'price': 89.99,
                'is_featured': True,
            },
            {
                'name': 'Tournament Edition Controller',
                'description': 'Competition-ready controller used by pro gamers.',
                'price': 179.99,
                'is_featured': True,
            },
        ]

        for controller in controllers:
            Controller.objects.create(
                name=controller['name'],
                slug=slugify(controller['name']),
                description=controller['description'],
                price=controller['price'],
                is_featured=controller['is_featured'],
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created controller: {controller["name"]}')
            ) 