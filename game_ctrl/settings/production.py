"""
Production settings for game_ctrl project.
"""

import os
from pathlib import Path
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/.env.prod')

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Import base settings
from .base import *  # noqa: F403

# Secret Key
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("DJANGO_SECRET_KEY is missing!")

# Debug settings
DEBUG = False

# Allowed Hosts
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,localhost:8000,127.0.0.1,127.0.0.1:8000').split(',')

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = [
    'https://gamesctrls.com',
    'https://www.gamesctrls.com',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# Security settings
SECURE_SSL_REDIRECT = False  # Temporarily disable for debugging
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = False  # Temporarily disable for debugging
CSRF_COOKIE_SECURE = False  # Temporarily disable for debugging
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'game_ctrl_db'),
        'USER': os.getenv('POSTGRES_USER', 'game_ctrl_user'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST', 'db'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

# Static & Media Files
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/static'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/media'

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://redis:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/game_ctrl.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}

# Sentry Configuration
if 'SENTRY_DSN' in os.environ:
    sentry_sdk.init(
        dsn=os.environ['SENTRY_DSN'],
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.5,
        send_default_pii=True,
        environment="production",
    )

