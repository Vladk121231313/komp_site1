from django.db import models
from catalog.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()

class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый заказ'),
        ('paid', 'Оплачен'),
        ('process', 'Сборка заказа'),
        ('shipped', 'Отправлен / В пути'),
        ('delivered', 'Доставлен'),
        ('canceled', 'Отменен'),
    ]

    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='orders', 
        verbose_name='Пользователь'
    )
    
    # --- НОВОЕ ПОЛЕ: СТАТУС ЗАКАЗА ---
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='new',
        verbose_name="Статус заказа"
    )

    first_name = models.CharField(max_length=50, verbose_name="Имя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    email = models.EmailField()
    address = models.CharField(max_length=250, verbose_name="Адрес")
    postal_code = models.CharField(max_length=20, verbose_name="Почтовый индекс")
    city = models.CharField(max_length=100, verbose_name="Город")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False, verbose_name="Оплата")
    
    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())
    
    def __str__(self):
        return f"Заказ №{self.id}"
    
    def get_total_quantity(self):
        """Считает общее количество всех товаров в заказе"""
        return sum(item.quantity for item in self.items.all())

    def get_total_cost(self):
        """Считает общую стоимость заказа"""
        return sum(item.get_cost() for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def get_cost(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product.name} ({self.quantity} шт.)"