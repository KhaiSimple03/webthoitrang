from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home,name = "home"),
    path('register/', views.register,name = "register"),
    path('search/',views.search,name ='search'),
    path('login/', views.loginPage,name = "login"),
    path('logout/', views.logoutPage,name = "logout"),
    path('cart/',views.cart,name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path('category/',views.category,name="category"),
    path('update_item/',views.updateItem, name = "update_item"),
    path('product/<int:product_id>/', views.detail, name='product_detail'),
    path('order/',views.order,name ="order"),
    path('api/check-stock/', views.check_stock, name='check_stock'),
    path('quick-checkout/', views.quick_checkout, name='quick_checkout'),
    path('orders/<int:order_id>/received/', views.mark_order_delivered, name='order_received'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('pay/', views.create_vnpay_url, name='create_vnpay_url'),
    path('payment_return/', views.payment_return, name='payment_return'),
    path('user_profile/',views.infor, name ='user_profile'),
    
    path('sanpham/<int:product_id>/',views.demosanpham, name= 'demosanpham'),
    path('thong_tin_giao_vien/',views.thong_tin_thay_co,name='thong_tin_giao_vien'),
]
