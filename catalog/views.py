from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from django.db.models import Q, Min, Max

def catalog_list(request, category_slug=None):
    query = request.GET.get('q')
    
    
    products = Product.objects.all() 
    
    categories = Category.objects.all()
    current_category = None
    
    # --- ЛОГИКА ФИЛЬТРАЦИИ КАТЕГОРИЙ ---
    category_params = request.GET.getlist('category')
    if category_params:
        # Разделяем ID (числа) и Slug (строки)
        ids = [val for val in category_params if val.isdigit()]
        slugs = [val for val in category_params if not val.isdigit()]
        
        q_objects = Q()
        if ids:
            q_objects |= Q(category_id__in=ids)
        if slugs:
            q_objects |= Q(category__slug__in=slugs)
            
        products = products.filter(q_objects)

    # Логика для URL-путей типа /catalog/cpu/
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=current_category)

    # --- ФИЛЬТР ПО ЦЕНЕ ---
    min_price_param = request.GET.get('min_price')
    max_price_param = request.GET.get('max_price')

    if min_price_param:
        try:
            products = products.filter(price__gte=int(min_price_param))
        except (ValueError, TypeError):
            pass

    if max_price_param:
        try:
            products = products.filter(price__lte=int(max_price_param))
        except (ValueError, TypeError):
            pass

    # Границы цен для ползунка
    price_bounds = Product.objects.aggregate(Min('price'), Max('price'))

    # --- ПОИСК ---
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).distinct()
    
    context = {
        'current_category': current_category,
        'categories': categories,
        'products': products,
        'price_bounds': price_bounds,
        'selected_min_price': min_price_param,
        'selected_max_price': max_price_param,
        'selected_categories': category_params, 
        'query': query, 
    }
    return render(request, 'catalog/catalog_list.html', context)

def product_detail(request, product_slug, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    # Используем select_related для оптимизации, чтобы подтянуть бренд и поставщика сразу
    product = get_object_or_404(Product.objects.select_related('manufacturer', 'supplier'), 
                                 slug=product_slug, category=category)
    context = {'product': product}
    return render(request, 'catalog/product_detail.html', context)

def index(request):
    # Берем последние 4 товара
    latest_products = Product.objects.all().order_by('-id')[:4]
    context = {
        'latest_products': latest_products
    }
    return render(request, 'catalog/index.html', context)