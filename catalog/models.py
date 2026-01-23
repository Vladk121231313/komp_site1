from django.db import models
from django.urls import reverse

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, verbose_name="Описание", null=True)
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True)
    
    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('catalog:catalog_list') + f'?category={self.slug}'

# --- НОВАЯ ТАБЛИЦА: ПОСТАВЩИКИ ---
class Supplier(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название компании")
    contact_person = models.CharField(max_length=100, verbose_name="Контактное лицо")
    contact_info = models.TextField(blank=True, verbose_name="Контактная информация", null=True)
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    address = models.TextField(verbose_name="Адрес склада", blank=True)

    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'

    def __str__(self):
        return self.name

class Product(models.Model):
    manufacturer = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name="Производитель")
    category = models.ForeignKey(Category, related_name='product', on_delete=models.CASCADE, verbose_name="Категория")
    
    # СВЯЗЬ С ПОСТАВЩИКОМ
    supplier = models.ForeignKey(
        Supplier, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='products',
        verbose_name="Поставщик"
    )

    name = models.CharField(max_length=100, verbose_name="Наименование")
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name='Описание', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    warranty_months = models.IntegerField(verbose_name="Гарантия (мес.)", null=True, blank=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d', verbose_name="Изображение", max_length=255)
    available = models.BooleanField(default=True, verbose_name="Доступен к продаже")
    
    # --- НОВОЕ ПОЛЕ: СКЛАД ---
    stock = models.PositiveIntegerField(default=0, verbose_name="Остаток на складе")

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name