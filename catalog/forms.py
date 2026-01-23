from django import forms
from .models import Product, Category, Brand, Supplier

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # Добавляем недостающие поля в список fields
        fields = [
            'category', 'manufacturer', 'supplier', 'name', 
            'slug', 'image', 'description', 'price', 
            'stock', 'warranty_months', 'available'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Автоматически добавляем Bootstrap класс всем полям формы
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        # Чекбокс должен иметь другой класс в Bootstrap
        self.fields['available'].widget.attrs.update({'class': 'form-check-input'})


# Базовый класс для красоты всех форм
class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if not isinstance(self.fields[field].widget, forms.CheckboxInput):
                self.fields[field].widget.attrs.update({'class': 'form-control'})
            else:
                self.fields[field].widget.attrs.update({'class': 'form-check-input'})

class CategoryForm(BootstrapModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug']

class ManufacturerForm(BootstrapModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'description']

class SupplierForm(BootstrapModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_info']