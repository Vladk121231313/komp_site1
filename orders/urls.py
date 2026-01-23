from django.urls import path, include
from . import views 

app_name = 'orders'

urlpatterns = [
    path('add/<slug:category_slug>/<slug:product_slug>/', views.add_to_cart, name='add_to_cart'),    path('cart/', views.cart_detail, name='cart_detail'),
    path('checkout/', views.checkout, name='checkout'),
    path('remove/<slug:product_slug>/', views.remove_from_cart, name='remove_from_cart'),
    path('history/', views.order_history, name='order_history'),
    path('profile/', views.user_profile, name='user_profile'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('custom-admin/', views.custom_admin_panel, name='custom_admin'),
    path('admin/update-stock/<int:product_id>/', views.update_stock, name='update_stock'),
    path('admin/delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('admin/delete-category/<int:pk>/', views.delete_category, name='delete_category'),
    path('admin/delete-manufacturer/<int:pk>/', views.delete_manufacturer, name='delete_manufacturer'),
    path('admin/delete-supplier/<int:pk>/', views.delete_supplier, name='delete_supplier'),
]