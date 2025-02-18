from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('add/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:controller_id>/', views.cart_remove, name='cart_remove'),
    path('update/', views.update_cart, name='update_cart'),
    path('', views.cart_detail, name='cart_detail'),
]