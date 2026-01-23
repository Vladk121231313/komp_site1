# orders/templatetags/orders_tags.py

from django import template

# Создаем объект Registry для регистрации наших тегов
register = template.Library()

# Сейчас мы просто оставим его пустым, чтобы зарегистрировать библиотеку.
# Нам пока не нужны кастомные теги, так как методы Order.get_total_cost и 
# OrderItem.get_subtotal вызываются напрямую.