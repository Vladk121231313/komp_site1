from django.urls import path, include
from . import views 

app_name = 'catalog'

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.catalog_list, name='catalog_list'),
    path('products/<slug:category_slug>/', views.catalog_list, name='catalog_list_by_category'),
    path('products/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
]