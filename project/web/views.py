from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Product, CategoryProduct

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        first_name = request.POST.get("first_name")
        user = authenticate(request, username=username, password=password, first_name=first_name)
        if user:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Неверные данные'})
    return render(request, 'login.html')
@login_required
def home_view(request):
    user = request.user
    if user.is_superuser:
        role = "Администратор"
    elif user.groups.filter(name="Менеджер").exists():
        role = "Менеджер"
    else:
        role = "Авторизованный пользователь"
    context = {
        "username": user.username,
        "first_name": user.first_name,
        "role": role
    }
    return render(request, "home.html", context)

def logout_view(request):
    logout(request)
    return redirect("login")

def product_list(request):
    products = Product.objects.all()
    return render(request, 'catalog.html', {'products': products})


def get_filtered_products(request):
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', '')
    category_id = request.GET.get('category', '')

    products = Product.objects.all().select_related('producer', 'manufacturer', 'category')

    if search_query:
        products = products.filter(
            Q(product__icontains=search_query) |
            Q(article__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(producer__name__icontains=search_query) |
            Q(manufacturer__name__icontains=search_query)
        )

    if category_id:
        products = products.filter(category_id=category_id)

    if sort_by == 'amount_asc':
        products = products.order_by('amount_on_warehouse')
    elif sort_by == 'amount_desc':
        products = products.order_by('-amount_on_warehouse')

    categories = CategoryProduct.objects.all()

    context = {
        'products': products,
        'search_query': search_query,
        'current_sort': sort_by,
        'current_category': category_id,
        'categories': categories,
        'total_products': products.count()
    }
    return render(request, 'search.html', context)