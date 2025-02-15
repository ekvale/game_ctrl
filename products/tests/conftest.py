import pytest
from django.conf import settings
from pathlib import Path
import shutil

@pytest.fixture(autouse=True)
def setup_static_files():
    """Ensure static files exist for tests."""
    static_dir = Path(settings.BASE_DIR) / 'static' / 'images'
    static_dir.mkdir(parents=True, exist_ok=True)
    
    # List of required SVG files
    svg_files = [
        'pro-fighter-x8.svg',
        'classic-arcade-plus.svg',
        'tournament-edition-pro.svg',
        'precision.svg',
        'customizable.svg',
        'durable.svg'
    ]
    
    # Create sample SVG content if files don't exist
    for svg_file in svg_files:
        svg_path = static_dir / svg_file
        if not svg_path.exists():
            with open(svg_path, 'w') as f:
                f.write(f'''
                <svg width="800" height="600" viewBox="0 0 800 600" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <!-- Main Controller Body -->
                    <rect x="100" y="100" width="600" height="400" rx="20" fill="#2D3436"/>
                    <!-- Joystick -->
                    <circle cx="250" cy="300" r="40" fill="#6C63FF"/>
                    <!-- 8 Button Layout -->
                    <circle cx="450" cy="250" r="25" fill="#00B894"/>
                    <!-- LED Strips -->
                    <rect x="120" y="120" width="560" height="10" rx="5" fill="#6C63FF"/>
                </svg>
                ''')

    yield

    # Cleanup after tests
    if static_dir.exists():
        shutil.rmtree(static_dir) 