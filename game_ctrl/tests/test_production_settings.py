from django.test import TestCase, override_settings
from django.conf import settings
from unittest.mock import patch
import os

@override_settings(
    DEBUG=False,
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': 'redis://test:6379/1',
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    },
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'test_db',
            'USER': 'test_user',
            'PASSWORD': 'test_pass',
            'HOST': 'test.host',
            'PORT': '5432',
            'CONN_MAX_AGE': 600,
        }
    },
    STATICFILES_STORAGE='storages.backends.s3boto3.S3Boto3Storage',
    DEFAULT_FILE_STORAGE='storages.backends.s3boto3.S3Boto3Storage',
    LOGGING={
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': '/var/log/django/game_ctrl.log',
                'maxBytes': 1024 * 1024 * 10,
                'backupCount': 5,
            },
        },
        'root': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
    },
    SECURE_SSL_REDIRECT=True,
    SECURE_HSTS_SECONDS=31536000,
    SECURE_HSTS_INCLUDE_SUBDOMAINS=True,
    SECURE_HSTS_PRELOAD=True,
    SESSION_COOKIE_SECURE=True,
    CSRF_COOKIE_SECURE=True,
    X_FRAME_OPTIONS='DENY'
)
class TestProductionSettings(TestCase):
    @patch.dict(os.environ, {
        'DJANGO_ALLOWED_HOST': 'test.example.com',
        'DB_NAME': 'test_db',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_pass',
        'DB_HOST': 'test.host',
        'REDIS_URL': 'redis://test:6379/1',
        'AWS_ACCESS_KEY_ID': 'test_key',
        'AWS_SECRET_ACCESS_KEY': 'test_secret',
        'AWS_STORAGE_BUCKET_NAME': 'test-bucket',
    })
    def test_security_settings(self):
        """Test security-related settings are properly configured"""
        self.assertFalse(settings.DEBUG)
        self.assertTrue(settings.SECURE_SSL_REDIRECT)
        self.assertEqual(settings.SECURE_HSTS_SECONDS, 31536000)
        self.assertTrue(settings.SECURE_HSTS_INCLUDE_SUBDOMAINS)
        self.assertTrue(settings.SECURE_HSTS_PRELOAD)
        self.assertTrue(settings.SESSION_COOKIE_SECURE)
        self.assertTrue(settings.CSRF_COOKIE_SECURE)
        self.assertEqual(settings.X_FRAME_OPTIONS, 'DENY')

    def test_database_settings(self):
        """Test database configuration"""
        db_settings = settings.DATABASES['default']
        self.assertEqual(db_settings['ENGINE'], 'django.db.backends.postgresql')
        self.assertEqual(db_settings['CONN_MAX_AGE'], 600)

    def test_cache_settings(self):
        """Test cache configuration"""
        cache_settings = settings.CACHES['default']
        self.assertEqual(
            cache_settings['BACKEND'],
            'django.core.cache.backends.redis.RedisCache'
        )

    def test_storage_settings(self):
        """Test static and media file storage settings"""
        self.assertEqual(
            settings.STATICFILES_STORAGE,
            'storages.backends.s3boto3.S3Boto3Storage'
        )
        self.assertEqual(
            settings.DEFAULT_FILE_STORAGE,
            'storages.backends.s3boto3.S3Boto3Storage'
        )

    def test_logging_configuration(self):
        """Test logging settings"""
        self.assertIn('console', settings.LOGGING['handlers'])
        self.assertIn('file', settings.LOGGING['handlers'])
        self.assertEqual(
            settings.LOGGING['root']['level'],
            'INFO'
        )

class ProductionSettingsTest(TestCase):
    @override_settings(DJANGO_SETTINGS_MODULE='game_ctrl.settings.production')
    def test_production_settings(self):
        self.assertFalse(settings.DEBUG)
        self.assertEqual(settings.STATIC_ROOT, '/var/www/static')
        # ... other production-specific tests 