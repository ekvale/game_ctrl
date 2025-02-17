"""
Production settings for game_ctrl project.
"""

import os
from pathlib import Path
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/.env.prod')  # Ensure this path is correct

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Import base settings
from .base import *  # noqa: F403

# Secret Key
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("DJANGO_SECRET_KEY is missing!")

# Debug settings
DEBUG = False  # Ensure Debug is OFF in production

# Allowed Hosts
ALLOWED_HOSTS = [
    'gamesctrls.com',
    'www.gamesctrls.com',
    'localhost',
    '127.0.0.1',
    'web',
    os.getenv("SERVER_IP", "137.184.8.118"),  # Ensure your server IP is included
]

# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'game_ctrl_db'),
        'USER': os.getenv('DB_USER', 'game_ctrl_user'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'db'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = [
    'https://gamesctrls.com',
    'https://www.gamesctrls.com',
]

# Static & Media Files
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/static'  # Ensure this is correctly mapped in Nginx
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/media'

# Enable WhiteNoise for serving static files
INSTALLED_APPS += ["whitenoise.runserver_nostatic"]
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Caching (Redis)
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
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Sentry Configuration (Optional)
if 'SENTRY_DSN' in os.environ:
    sentry_sdk.init(
        dsn=os.environ['SENTRY_DSN'],
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.5,
        send_default_pii=True,
        environment="production",
    )

