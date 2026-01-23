from django.shortcuts import HttpResponse, get_object_or_404,redirect, render
from catalog.models import Product, Category, Brand, Supplier
from .models import Order, OrderItem
from .forms import OrderCreateForm, CartAddQuantityForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from django.db.models import Sum
from django.db import transaction
from catalog.forms import ProductForm, CategoryForm, ManufacturerForm, SupplierForm

# --- ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ ---
@login_required
def user_profile(request):
    # Получаем все заказы текущего пользователя
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/profile.html', {
        'orders': orders
    })

# --- ПАНЕЛЬ АДМИНИСТРАТОРА (Только для персонала) ---
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    # 1. Считаем общую выручку (только оплаченные заказы)
    total_revenue = Order.objects.filter(paid=True).aggregate(total=Sum('items__price'))['total'] or 0
    
    # 2. Товары, которые заканчиваются на складе (меньше 5 шт)
    low_stock_products = Product.objects.filter(stock__lt=5)
    
    # 3. Последние 10 проданных товаров для отчета
    recent_sales = OrderItem.objects.select_related('order', 'product').filter(order__paid=True).order_by('-order__created_at')[:10]
    
    # 4. Общее кол-во заказов
    orders_count = Order.objects.count()

    return render(request, 'orders/admin_dashboard.html', {
        'total_revenue': total_revenue,
        'low_stock': low_stock_products,
        'recent_sales': recent_sales,
        'orders_count': orders_count
    })


@user_passes_test(lambda u: u.is_staff)
def custom_admin_panel(request):
    # Подготавливаем контекст (как было раньше)
    context = {
        'products': Product.objects.all().order_by('-id'),
        'categories': Category.objects.all(),
        'manufacturers': Brand.objects.all(),
        'suppliers': Supplier.objects.all(),
        'p_form': ProductForm(),
        'c_form': CategoryForm(),
        'm_form': ManufacturerForm(),
        's_form': SupplierForm(),
    }

    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        form = None 
        if form_type == 'product':
            form = ProductForm(request.POST, request.FILES)
        elif form_type == 'category':
            form = CategoryForm(request.POST)
        elif form_type == 'manufacturer':
            form = ManufacturerForm(request.POST)
        elif form_type == 'supplier':
            form = SupplierForm(request.POST)

        if form and form.is_valid():
            form.save()
            messages.success(request, "Запись успешно добавлена!")
            return redirect('orders:custom_admin')
        else:
            messages.error(request, "Ошибка при заполнении формы.")
            if form_type == 'product': context['p_form'] = form
            elif form_type == 'category': context['c_form'] = form
            elif form_type == 'manufacturer': context['m_form'] = form
            elif form_type == 'supplier': context['s_form'] = form

    return render(request, 'orders/custom_admin.html', context)

@require_POST
@user_passes_test(lambda u: u.is_staff)
def update_stock(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    action = request.POST.get('action')
    
    if action == 'increment':
        product.stock += 1
    elif action == 'decrement' and product.stock > 0:
        product.stock -= 1
    
    product.save()
    return JsonResponse({'new_stock': product.stock})

@user_passes_test(lambda u: u.is_staff)
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, f"Товар {product.name} удален")
    return redirect('orders:custom_admin')

@user_passes_test(lambda u: u.is_staff)
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, f'Категория "{category.name}" успешно удалена.')
    return redirect('orders:custom_admin') # Замени на свой URL админки

@user_passes_test(lambda u: u.is_staff)
def delete_manufacturer(request, pk):
    obj = get_object_or_404(Brand, pk=pk)
    obj.delete()
    messages.success(request, 'Производитель удален.')
    return redirect('orders:custom_admin')

@user_passes_test(lambda u: u.is_staff)
def delete_supplier(request, pk):
    obj = get_object_or_404(Supplier, pk=pk)
    obj.delete()
    messages.success(request, 'Поставщик удален.')
    return redirect('orders:custom_admin')

# Create your views here.
@login_required
def add_to_cart(request, category_slug, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    # 1. Проверка наличия
    if product.stock <= 0:
        if is_ajax: return JsonResponse({'error': 'Нет в наличии'}, status=400)
        return redirect(request.META.get('HTTP_REFERER', 'catalog:catalog_list'))

    # 2. Получаем или создаем КОРЗИНУ (незавершенный заказ)
    # Используем filter().first(), чтобы избежать ошибки MultipleObjectsReturned
    order = Order.objects.filter(user=request.user, paid=False).first()
    
    if not order:
        # Важно: если в модели Order поля обязательные, Django может выдать 500 ошибку здесь.
        # Создаем пустой заказ, привязанный к юзеру.
        order = Order.objects.create(
            user=request.user,
            paid=False,
            status='created'
            # Если будут ошибки — проверь, чтобы в models.py у полей адреса стояло null=True, blank=True
        )
    
    request.session['order_id'] = order.id

    if request.method == 'POST':
        # Получаем кол-во (из каталога обычно 1, из корзины может быть больше)
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            quantity = 1

        # Создаем или обновляем позицию в заказе
        order_item, created = OrderItem.objects.get_or_create(
            order=order,
            product=product,
            defaults={'price': product.price, 'quantity': quantity}
        )
        
        if not created:
            # Если запрос пришел через AJAX (из корзины), 
            # мы перезаписываем количество тем, что ввел пользователь
            if is_ajax:
                order_item.quantity = quantity
            else:
                # Если это обычный переход по ссылке (из каталога), 
                # то просто добавляем +1 к имеющемуся
                order_item.quantity += quantity
            
            # Проверка на наличие на складе, чтобы не заказали больше возможного
            if order_item.quantity > product.stock:
                order_item.quantity = product.stock
                
            order_item.save()

        if is_ajax:
            # Считаем, удален ли товар (если вдруг количество стало 0 или меньше)
            item_deleted = False
            if order_item.quantity <= 0:
                order_item.delete()
                item_deleted = True

            return JsonResponse({
                'status': 'ok',
                'item_deleted': item_deleted,
                'item_cost': "{:.2f}".format(order_item.get_cost()) if not item_deleted else 0,
                'cart_total_quantity': order.get_total_quantity(),
                'cart_total_cost': "{:.2f}".format(order.get_total_cost()),
                'product_slug': product.slug
            })

    return redirect(request.META.get('HTTP_REFERER', 'orders:cart_detail'))

def cart_detail(request):
    # 1. Получаем order_id из сессии.
    order_id = request.session.get('order_id')
    
    # 2. Если ID есть, получаем объект Order.
    if order_id:
        # get_object_or_404 сам вызовет 404, если ID не существует (что мы и видели ранее)
        order = get_object_or_404(Order, id=order_id)
        # Получаем все товары, связанные с этим заказом
        cart_items = OrderItem.objects.filter(order=order)
        
        for item in cart_items:
            item.update_quantity_form = CartAddQuantityForm(initial={'quantity':item.quantity, 'update':True})

        # Обрати внимание: мы ожидаем, что у объекта Order есть метод get_total_cost()
        # Если его нет, нам нужно будет его добавить в orders/models.py позже.
        total_cost = order.get_total_cost() if hasattr(order, 'get_total_cost') else sum(item.get_cost() for item in cart_items)
        
    else:
        # Если order_id нет (корзина пуста)
        order = None
        cart_items = []
        total_cost = 0

    return render(request, 'orders/cart_detail.html', {
        'order': order,
        'cart_items': cart_items,
        'total_cost': total_cost,
    })

@login_required
def checkout(request):
    """Оформление заказа со списанием остатков"""
    order_id = request.session.get('order_id')
    if not order_id:
        return redirect('catalog:catalog_list') 
    
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST, instance=order) 
        if form.is_valid():
            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    order.user = request.user 
                    order.paid = True 
                    order.status = 'paid' # Меняем статус для отслеживания
                    order.save() 

                    for item in order.items.all():
                        product = item.product
                        if product.stock < item.quantity:
                            raise ValueError(f'Товар {product.name} закончился')
                        
                        product.stock -= item.quantity
                        product.save()

                    del request.session['order_id']
                    messages.success(request, 'Заказ успешно оформлен!')
                    return redirect('/')
            except ValueError as e:
                messages.error(request, str(e))
                return redirect('orders:cart_detail')
    else:
        form = OrderCreateForm(initial={'email': request.user.email})
    
    return render(request, 'orders/checkout.html', {'form': form, 'order': order})

def remove_from_cart(request, product_slug):
    product = get_object_or_404(Product, slug = product_slug)
    order = None
    order_id = request.session.get('order_id')
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            pass
    if order:
        item_to_remove = get_object_or_404(
            OrderItem,
            order=order,
            product=product
        )
        item_to_remove.delete()
    referer_url = request.META.get('HTTP_REFERER')
    
    # 2. Если referer_url существует, используем его. 
    # Иначе, на всякий случай, перенаправляем на каталог.
    if referer_url:
        return redirect(referer_url)
    else:
        return redirect('orders:cart_detail') # Безопасный запасной вариант


@login_required
def order_history(request):
    # Получаем все заказы, связанные с текущим пользователем, и сортируем их по дате создания
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'orders/order_history.html', {'orders': orders})