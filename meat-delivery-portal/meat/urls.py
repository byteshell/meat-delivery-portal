from django.urls import path
from . import views
from .views import meat_list, add_meat, company_dashboard, company_meat_orders
from orders.views import update_cart

urlpatterns = [
    path('', views.meat_list, name='meat_list'),
    path('add/', views.add_meat, name='add_meat'),
    path('company/', views.company_dashboard, name='company_dashboard'),
    path('company/meat-orders/', views.company_meat_orders, name='company_meat_orders'),
    path('orders/update-cart/', update_cart, name='update_cart'),
]
