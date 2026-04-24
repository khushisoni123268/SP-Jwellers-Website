from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import RegisterForm
from .models import Category, Order, OrderItem, Product


def home(request):
    featured_products = Product.objects.filter(available=True, featured=True)[:8]
    categories = Category.objects.all()[:6]
    return render(request, 'shop/home.html', {
        'featured_products': featured_products,
        'categories': categories
    })


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully. Welcome to SP Jewellers!')
            return redirect('dashboard')
    else:
        form = RegisterForm()

    return render(request, 'shop/register.html', {'form': form})


@login_required
def dashboard(request):
    user_email = (request.user.email or '').strip()
    recent_orders = Order.objects.none()

    if user_email:
        recent_orders = Order.objects.filter(email__iexact=user_email).order_by('-created_at')[:5]

    return render(request, 'shop/dashboard.html', {
        'recent_orders': recent_orders,
        'has_email': bool(user_email),
    })


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    q = request.GET.get('q')
    if q:
        products = products.filter(name__icontains=q)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    return render(request, 'shop/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products
    })


def product_detail(request, category_slug, product_slug):
    product = get_object_or_404(
        Product,
        category__slug=category_slug,
        slug=product_slug,
        available=True
    )
    return render(request, 'shop/product_detail.html', {'product': product})


def get_cart_data(request):
    cart = request.session.get('cart', {})
    items = []
    total = Decimal('0.00')

    products = Product.objects.filter(id__in=cart.keys())

    for product in products:
        quantity = int(cart[str(product.id)])
        subtotal = product.price * quantity
        total += subtotal
        items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    return items, total


def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    request.session['cart'] = cart
    return redirect('cart_detail')


def cart_detail(request):
    items, total = get_cart_data(request)
    return render(request, 'shop/cart.html', {
        'items': items,
        'total': total
    })


def update_cart(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        product_id = str(product_id)
        quantity = int(request.POST.get('quantity', 1))

        if quantity > 0:
            cart[product_id] = quantity
        else:
            cart.pop(product_id, None)

        request.session['cart'] = cart

    return redirect('cart_detail')


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    cart.pop(product_id, None)
    request.session['cart'] = cart
    return redirect('cart_detail')


def checkout(request):
    items, total = get_cart_data(request)

    if not items:
        return redirect('product_list')

    prefill_name = request.POST.get('full_name', '')
    prefill_email = request.POST.get('email', '')

    if request.user.is_authenticated:
        if not prefill_name:
            prefill_name = request.user.get_full_name() or request.user.username
        if not prefill_email:
            prefill_email = request.user.email

    if request.method == 'POST':
        order = Order.objects.create(
            full_name=request.POST.get('full_name') or prefill_name,
            email=request.POST.get('email') or prefill_email,
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            city=request.POST.get('city'),
            paid=False
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                price=item['product'].price,
                quantity=item['quantity']
            )

        request.session['cart'] = {}
        return render(request, 'shop/success.html', {'order': order})

    return render(request, 'shop/checkout.html', {
        'items': items,
        'total': total,
        'prefill_name': prefill_name,
        'prefill_email': prefill_email,
    })
