from django.contrib import admin
from .models import Order, OrderItem

# 1. Определяем класс, как будут отображаться пункты заказа (OrderItem)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    # Поля, которые пользователь увидит в таблице:
    fields = ('product', 'price', 'quantity')
    # Это позволяет искать продукт по ID, а не загружать весь список (для производительности):
    raw_id_fields = ['product'] 
    
# 2. Определяем класс для самого Заказа (Order)
class OrderAdmin(admin.ModelAdmin):
    # Отображаем OrderItemInlines внутри формы редактирования Order:
    inlines = [OrderItemInline]
    # Указываем, какие поля видеть в списке Order:
    list_display = ('id', 'created_at')

# 3. Регистрируем Order с нашим кастомным классом
admin.site.register(Order, OrderAdmin)
# OrderItem не нужно регистрировать отдельно, так как он управляется через OrderAdmin