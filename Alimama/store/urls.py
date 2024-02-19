from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


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
    path('delete_account/', views.delete_account, name='delete_account'),
    # URLs for password reset
    path('password_reset/', auth_views.PasswordResetView.as_view(),
         name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),

]
