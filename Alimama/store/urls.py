from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('<slug:category_slug>', views.home, name='products_by_category'),
    path('product/', views.product, name='product'),
]
