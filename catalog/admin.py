from django.contrib import admin
from .models import Brand, Product, Category, Supplier

# 1. Регистрация категорий
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)} 

# 2. Регистрация поставщиков
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'phone', 'email']
    search_fields = ['name']

# 3. Регистрация товаров
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Выводим все важные поля, включая остаток и поставщика
    list_display = ['name', 'price', 'stock', 'supplier', 'category', 'available']
    list_filter = ['available', 'category', 'supplier', 'manufacturer']
    # Позволяет менять цену, остаток и наличие прямо в списке, не заходя внутрь товара
    list_editable = ['price', 'stock', 'available'] 
    prepopulated_fields = {'slug': ('name',)}

# 4. Регистрация брендов (простая регистрация)
admin.site.register(Brand)