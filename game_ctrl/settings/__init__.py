"""
Settings package initialization.
This file can be empty, but it's required for Python to treat the directory as a package.
"""
import os

# Set the default Django settings module
settings_module = os.getenv('DJANGO_SETTINGS_MODULE', 'game_ctrl.settings.production')
if settings_module:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

# Empty file to make settings a package 