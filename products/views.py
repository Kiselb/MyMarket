from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from basket.forms import CartAddProductForm

def product_list(request, category_id=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(stock__gt=0)
    
    if category_id:
        category = get_object_or_404(Category, id=category_id)
        products = products.filter(category=category)
    
    return render(request, 'products/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products,
    })

# def product_detail(request, id, slug):
#     product = get_object_or_404(Product, id=id, slug=slug, stock__gt=0)
#     cart_product_form = CartAddProductForm()
#     return render(request, 'products/product_detail.html', {
#         'product': product,
#         'cart_product_form': cart_product_form,
#     })

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'products/product_detail.html', {'product': product})
