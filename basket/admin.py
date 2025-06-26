from django.contrib import admin
from .models import Cart, CartItem

class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']
    list_filter = ['user', 'created_at']
    search_filters = ['user', 'created_at']

admin.site.register(Cart, CartAdmin)

class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity']
    list_filter = ['cart', 'product', 'quantity']
    search_filters = ['cart', 'product', 'quantity']

admin.site.register(CartItem, CartItemAdmin)
