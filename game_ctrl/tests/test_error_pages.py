from django.urls import reverse, path, include
from django.test import SimpleTestCase, override_settings
from django.http import HttpResponse, HttpResponseServerError
from django.views import View
from django.core.exceptions import ViewDoesNotExist
from django.contrib.auth import views as auth_views

@override_settings(DEBUG=False)
class TestErrorPages(SimpleTestCase):
    def setUp(self):
        self.original_urlconf = getattr(self.client, 'urlconf', None)

    def tearDown(self):
        if self.original_urlconf:
            self.client.urlconf = self.original_urlconf

    def create_test_urlconf(self):
        """Create a test URLconf with all required namespaces"""
        # Products URLs
        products_urls = ([
            path('', lambda r: HttpResponse(), name='home'),
            path('test-500/', lambda r: HttpResponse(), name='test'),
        ], 'products')

        # Cart URLs
        cart_urls = ([
            path('', lambda r: HttpResponse(), name='cart_detail'),
        ], 'cart')

        # Auth URLs
        auth_urls = [
            path('login/', auth_views.LoginView.as_view(), name='login'),
        ]

        # Main URLconf
        urlpatterns = [
            path('', include(products_urls)),
            path('cart/', include(cart_urls)),
            path('accounts/', include(auth_urls)),
        ]

        return type('URLModule', (), {'urlpatterns': urlpatterns})

    def test_404_page(self):
        """Test 404 page is rendered correctly"""
        with override_settings(ROOT_URLCONF=self.create_test_urlconf()):
            response = self.client.get('/nonexistent-page/', secure=True)
            self.assertEqual(response.status_code, 404)
            self.assertIn(b"Page Not Found", response.content)
            self.assertIn(b"Return Home", response.content)

    def test_500_page(self):
        """Test 500 page is rendered correctly"""
        class ErrorView(View):
            def get(self, request):
                raise ViewDoesNotExist("Test error")

        # Create test URLs with all namespaces
        products_urls = ([
            path('', lambda r: HttpResponse(), name='home'),
            path('test-500/', ErrorView.as_view(), name='test'),
        ], 'products')

        cart_urls = ([
            path('', lambda r: HttpResponse(), name='cart_detail'),
        ], 'cart')

        auth_urls = [
            path('login/', auth_views.LoginView.as_view(), name='login'),
        ]

        # Create a test URLconf module
        urlpatterns = [
            path('', include(products_urls)),
            path('cart/', include(cart_urls)),
            path('accounts/', include(auth_urls)),
        ]

        # Create a module-like object
        mod = type('URLModule', (), {'urlpatterns': urlpatterns})

        # Use the test URLconf
        with override_settings(ROOT_URLCONF=mod):
            response = self.client.get('/test-500/', secure=True)
            self.assertEqual(response.status_code, 500)
            self.assertIn(b"Server Error", response.content)
            self.assertIn(b"Something went wrong", response.content)

    def test_error_page_links(self):
        """Test that error pages have working home links"""
        with override_settings(ROOT_URLCONF=self.create_test_urlconf()):
            response = self.client.get('/nonexistent-page/', secure=True)
            self.assertEqual(response.status_code, 404)
            self.assertIn(bytes(reverse('products:home'), 'utf-8'), response.content)
            self.assertIn(bytes(reverse('cart:cart_detail'), 'utf-8'), response.content) 