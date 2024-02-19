from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('category/<slug:category_slug>',
         views.home, name='products_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>',
         views.product, name='product_detail'),
    path('cart/add/<int:product_id>', views.add_cart, name='add_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/remove/<int:product_id>', views.cart_remove, name='cart_remove'),
    path('cart/delete_cart_item/<int:product_id>',
         views.delete_cart_item, name='delete_cart_item'),
    path('success/<int:order_id>', views.success_view, name='success_view'),
    path('account/create/', views.signupView, name='signup'),
    path('account/signin/', views.signinView, name='signin'),
    path('account/signout/', views.signoutView, name='signout'),
    path('userdashboard/', views.userDashboard, name='user_dashboard'),
    path('order/<int:order_id>', views.viewOrder, name='order_detail'),
    path('search/', views.search, name='search'),
]
