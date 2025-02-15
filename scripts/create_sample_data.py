from django.core.files import File
from products.models import Category, Controller
from django.contrib.auth import get_user_model
from pathlib import Path
import os

def create_sample_data():
    # Create categories
    arcade = Category.objects.create(
        name="Arcade Controllers",
        slug="arcade-controllers"
    )
    
    # Base path for images
    image_path = Path('media/controllers/2025/02/15')
    image_path.mkdir(parents=True, exist_ok=True)
    
    # Create controllers with images
    with open('static/images/pro-fighter-x8.jpg', 'rb') as f:
        Controller.objects.create(
            category=arcade,
            name="Pro Fighter X8",
            slug="pro-fighter-x8",
            description="Professional-grade arcade controller featuring 8 Sanwa buttons, authentic arcade joystick, and customizable LED lighting. Perfect for fighting games and retro arcade classics.",
            price=199.99,
            available=True,
            image=File(f, name='pro-fighter-x8.jpg')
        )
    
    with open('static/images/classic-arcade-plus.jpg', 'rb') as f:
        Controller.objects.create(
            category=arcade,
            name="Classic Arcade Plus",
            slug="classic-arcade-plus",
            description="Traditional arcade layout with 6 primary buttons, 2 macro buttons, and a competition-grade joystick. Features turbo functionality and button mapping.",
            price=149.99,
            available=True,
            image=File(f, name='classic-arcade-plus.jpg')
        )
    
    with open('static/images/tournament-edition-pro.jpg', 'rb') as f:
        Controller.objects.create(
            category=arcade,
            name="Tournament Edition Pro",
            slug="tournament-edition-pro",
            description="Tournament-ready controller with premium Seimitsu buttons, optical joystick, and zero input lag. Includes carrying case and cable management.",
            price=249.99,
            available=True,
            image=File(f, name='tournament-edition-pro.jpg')
        )

if __name__ == "__main__":
    create_sample_data() 