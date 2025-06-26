from django.contrib import admin
from .models import Product
from .models import Category
from .models import Order
from .models import OrderItem
from .models import Review

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'price', 'stock', 'category', 'created_at']
    list_filter = ['name', 'description', 'price', 'stock', 'category', 'created_at']
    search_filters = ['name', 'description']

admin.site.register(Product, ProductAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'parent']
    list_filter = ['name', 'description', 'parent']
    search_filters = ['name', 'description']

admin.site.register(Category, CategoryAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'status']
    list_filter = ['user', 'created_at', 'status']
    search_filters = ['user', 'created_at', 'status']

admin.site.register(Order, OrderAdmin)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']
    list_filter = ['order', 'product', 'quantity', 'price']
    search_filters = ['order', 'product', 'quantity', 'price']

admin.site.register(OrderItem, OrderItemAdmin)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'text', 'created_at']
    list_filter = ['product', 'user', 'rating', 'text', 'created_at']
    search_filters = ['product', 'user', 'rating', 'text']

admin.site.register(Review, ReviewAdmin)
