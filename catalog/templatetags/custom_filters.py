# catalog/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Позволяет получить значение из словаря по ключу."""
    return dictionary.get(key)