from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from .models import Product, Interaction
from .recommend import get_similar_products, get_homepage_picks, model_is_ready


def home(request):
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    products = Product.objects.all()
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(brand__icontains=query) | Q(category__icontains=query)
        )
    if category:
        products = products.filter(category__icontains=category)

    personalized = None
    if not query and not category:
        personalized = get_homepage_picks(request.user, top_n=8)

    paginator = Paginator(products, 24)
    page_obj = paginator.get_page(request.GET.get('page'))

    top_categories = ['household', 'personal care', 'health', 'hair', 'makeup', 'men']

    return render(request, 'store/home.html', {
        'page_obj': page_obj,
        'query': query,
        'active_category': category,
        'top_categories': top_categories,
        'personalized': personalized,
        'model_ready': model_is_ready(),
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    similar = get_similar_products(product.id, top_n=8)

    if request.user.is_authenticated:
        Interaction.objects.get_or_create(
            user=request.user, product=product, action=Interaction.VIEW
        )

    return render(request, 'store/product_detail.html', {
        'product': product,
        'similar': similar,
    })


def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'store/register.html', {'form': form})
