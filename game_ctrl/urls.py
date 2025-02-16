from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView, TemplateView
from .health_checks import health_check
from django.contrib.auth import views as auth_views
from django.shortcuts import render

def test_video(request):
    return render(request, 'marketing/test_video.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('', include('products.urls')),
    path('cart/', include('cart.urls')),
    
    # Auth URLs
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', TemplateView.as_view(template_name='registration/register.html'), name='register'),
    path('test-video/', test_video, name='test_video'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 