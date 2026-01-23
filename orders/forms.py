# orders/forms.py
from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        # Поля, которые мы хотим видеть в форме для заполнения пользователем
        fields = ['first_name', 'last_name', 'email', 'address', 'postal_code', 'city']
        
        # Опционально: можно настроить отображаемые метки (labels)
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Email',
            'address': 'Адрес доставки',
            'postal_code': 'Почтовый индекс',
            'city': 'Город',
        }

# 2. Форма для изменения количества в корзине (Standard Form)
class CartAddQuantityForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1, 
        max_value=99,
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm text-center', 'style': 'width: 70px;'}),
        initial=1
    )
    
    # Скрытое поле, которое всегда отправляется как True (для нашего Update)
    update = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.HiddenInput
    )