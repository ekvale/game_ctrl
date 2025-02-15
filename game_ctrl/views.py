from django.http import HttpResponseToo
from django.core.cache import cache
from django.conf import settings

def rate_limit_view(request, exception):
    """View to handle rate limited requests"""
    return HttpResponseTooMany(
        "Too many requests. Please try again later.",
        content_type="text/plain"
    ) 