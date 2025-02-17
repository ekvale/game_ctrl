from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.shortcuts import render

from products.views import home
from .health_checks import health_check

def test_video(request):
    return render(request, 'marketing/test_video.html')

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Health Check
    path('health/', health_check, name='health_check'),
    
    # Main URLs
    path('', home, name='home'),
    path('products/', include('products.urls')),  # Changed from empty string
    path('cart/', include('cart.urls')),

    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', TemplateView.as_view(template_name='registration/register.html'), name='register'),
    
    # Marketing/Testing
    path('test-video/', test_video, name='test_video'),
]

# Serve static/media files in development only
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 