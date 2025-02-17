"""
WSGI config for game_ctrl project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game_ctrl.settings.production')

application = get_wsgi_application() 