from django.test import RequestFactory, SimpleTestCase
from django.http import HttpResponse
from game_ctrl.middleware import ErrorHandlingMiddleware
from unittest.mock import patch

class TestErrorHandlingMiddleware(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        
        def get_response(request):
            return HttpResponse()
            
        self.middleware = ErrorHandlingMiddleware(get_response)

    def test_normal_request(self):
        """Test middleware passes through normal requests"""
        response = self.middleware(self.request)
        assert response.status_code == 200

    def test_exception_handling(self):
        """Test middleware handles exceptions properly"""
        with patch('game_ctrl.middleware.logger') as mock_logger:
            exception = Exception("Test error")
            response = self.middleware.process_exception(self.request, exception)
            
            # Verify logging
            mock_logger.exception.assert_called_once_with("Unhandled exception occurred")
            
            # Verify response
            assert response.status_code == 500
            assert b"Server Error" in response.content

    def test_template_rendering(self):
        """Test error template is rendered correctly"""
        response = self.middleware.process_exception(self.request, Exception())
        content = response.content.decode('utf-8')
        
        assert "500" in content
        assert "Server Error" in content
        assert "Something went wrong" in content 