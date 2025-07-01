from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='home'),
    path('category/<int:category_id>/', views.product_list, name='product_list_by_category'),
    path('<int:id>/', views.product_detail, name='product_detail'),
]
