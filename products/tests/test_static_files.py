import pytest
from django.conf import settings
from pathlib import Path
import os
import shutil

class TestStaticFiles:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        # Create static directories
        static_dir = Path(settings.BASE_DIR) / 'static' / 'images'
        static_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy SVG files to static directory if they don't exist
        for svg_file in ['pro-fighter-x8.svg', 'classic-arcade-plus.svg', 
                        'tournament-edition-pro.svg', 'precision.svg', 
                        'customizable.svg', 'durable.svg']:
            source = Path(__file__).parent.parent / 'static' / 'images' / svg_file
            if source.exists():
                shutil.copy(source, static_dir / svg_file)
    
    def test_svg_files_exist(self):
        static_dir = Path(settings.BASE_DIR) / 'static'
        required_svgs = [
            'images/pro-fighter-x8.svg',
            'images/classic-arcade-plus.svg',
            'images/tournament-edition-pro.svg',
            'images/precision.svg',
            'images/customizable.svg',
            'images/durable.svg',
        ]
        
        for svg_path in required_svgs:
            full_path = static_dir / svg_path
            assert full_path.exists(), f"SVG file missing: {svg_path}"
    
    def test_svg_file_content(self):
        static_dir = Path(settings.BASE_DIR) / 'static'
        svg_path = static_dir / 'images/pro-fighter-x8.svg'
        
        with open(svg_path, 'r') as f:
            content = f.read()
            assert 'viewBox="0 0 800 600"' in content
            assert 'Main Controller Body' in content
            assert 'Joystick' in content
            assert '8 Button Layout' in content
            assert 'LED Strips' in content 