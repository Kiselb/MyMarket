from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from products.models import Product
from .models import Cart, CartItem
from .forms import CartAddProductForm
from .cart import SessionCart

def get_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return cart
    return SessionCart(request)

def login_and_merge_cart(request, user):
    session_cart = SessionCart(request)
    if session_cart:
        session_cart.merge_to_user_cart(user)
    login(request, user)
    return redirect('profile')

@require_POST
def cart_add(request, product_id):
    cart = get_cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)

    print("POST data:", request.POST)
    print("Form errors:", form.errors if not form.is_valid() else "No errors")
    print(f'CartAddProductForm validity: {form.is_valid()}')

    if not form.is_valid():
        from pprint import pprint
        print("Invalid form data:")
        pprint(form.errors)
        return render(request, 'cart/debug.html', {
            'post_data': request.POST,
            'form_errors': form.errors
        })
    
    if form.is_valid():
        cd = form.cleaned_data
        if isinstance(cart, SessionCart):
            cart.add(
                product=product,
                quantity=cd['quantity'],
                override_quantity=cd['override']
            )
            messages.success(request, "Товар добавлен в корзину")
        else:
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': cd['quantity']}
            )
            if not created:
                if cd['override']:
                    cart_item.quantity = cd['quantity']
                else:
                    cart_item.quantity += cd['quantity']
                cart_item.save()
            messages.success(request, "Товар обновлён в корзине")
    else:
        messages.error(request, "Ошибка при добавлении товара в корзину")
    return redirect('cart:cart_detail')

@require_POST
def cart_remove(request, product_id):
    cart = get_cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    if isinstance(cart, SessionCart):
        cart.remove(product)
    else:
        CartItem.objects.filter(cart=cart, product=product).delete()
    
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = get_cart(request)
    
    if isinstance(cart, SessionCart):
        cart_items = list(cart)
        for item in cart_items:
            item['update_form'] = CartAddProductForm(initial={
                'quantity': item['quantity'],
                'override': True
            })
    else:
        cart_items = cart.items.select_related('product').all()
        for item in cart_items:
            item.update_form = CartAddProductForm(initial={
                'quantity': item.quantity,
                'override': True
            })
    
    return render(request, 'cart/detail.html', {
        'cart': cart,
        'cart_items': cart_items
    })
