import pytest
from django.test import Client
from django.urls import reverse
from django.core.cache import cache
from django.db import connection
from unittest.mock import patch

@pytest.mark.django_db
class TestHealthChecks:
    def test_health_check_success(self, client):
        response = client.get('/health/', secure=True)
        assert response.status_code == 200
        assert response.content.decode() == 'ok'
    
    @patch('django.db.connection.cursor')
    def test_health_check_db_failure(self, mock_cursor, client):
        mock_cursor.side_effect = Exception('DB Error')
        response = client.get('/health/', secure=True)
        assert response.status_code == 500
        assert 'DB Error' in response.content.decode()
    
    @patch('django.core.cache.cache.set')
    def test_health_check_cache_failure(self, mock_cache, client):
        mock_cache.side_effect = Exception('Cache Error')
        response = client.get('/health/', secure=True)
        assert response.status_code == 500
        assert 'Cache Error' in response.content.decode() 