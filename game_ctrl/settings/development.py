from .base import *

DEBUG = True
SECRET_KEY = 'django-insecure-development-key'
ALLOWED_HOSTS = ['*']

# Use local storage for development
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media' 