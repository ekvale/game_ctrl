from django.http import HttpResponseServerError, Http404
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as e:
            return self.process_exception(request, e)

    def process_exception(self, request, exception):
        # Don't handle 404 exceptions
        if isinstance(exception, Http404):
            raise

        # Log the error
        logger.exception("Unhandled exception occurred")

        # Render custom error template
        template = render_to_string('500.html')
        return HttpResponseServerError(template) 