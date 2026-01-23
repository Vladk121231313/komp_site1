# orders/context_processors.py

from .models import Order, OrderItem
from django.db.models import Sum

def cart_count(request):
    """
    Контекстный процессор, который добавляет общее количество 
    товаров в корзине в контекст шаблона.
    """
    total_quantity = 0
    order_id = request.session.get('order_id')
    
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
            total = OrderItem.objects.filter(order=order).aggregate(sum_qty=Sum('quantity'))
            total_quantity = total['sum_qty'] if total['sum_qty'] else 0
            
        except Order.DoesNotExist:
            pass
            
    return {'cart_total_quantity': total_quantity}

def cart_status(request):
    """
    Добавляет список SLUG'ов товаров, находящихся в текущей корзине, 
    в контекст каждого запроса.
    """

    cart_items_quantities = {}
    items_in_cart_slugs = set()
    order_id = request.session.get('order_id')
    

    if order_id:
        try:
            # Находим все OrderItem для текущего заказа и получаем SLUGs связанных товаров
            items = OrderItem.objects.filter(order_id=order_id).select_related('product')
            
            for item in items:
                slug = item.product.slug
                quantity = item.quantity
                
                # Заполняем оба словаря/множества
                items_in_cart_slugs.add(slug)
                cart_items_quantities[slug] = quantity

            items_in_cart_slugs = {item.product.slug for item in items}
            
        except Order.DoesNotExist:
            pass
        except Exception as e:
            pass

    return {
        'items_in_cart_slugs': items_in_cart_slugs,
        'items_in_cart_quantities': cart_items_quantities,
    }