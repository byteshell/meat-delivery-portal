from django.urls import path
from . import views
from .views import meat_list, add_meat, company_dashboard, company_meat_orders, home
from orders.views import update_cart

app_name = "meat"

urlpatterns = [
    path('', meat_list, name='meat_list'),  # /meat/ shows meat list, name is 'meat_list'
    path('home/', home, name='home'),       # /meat/home/ for landing page (optional)
    path('add/', add_meat, name='add_meat'),
    path('company/', company_dashboard, name='company_dashboard'),
    path('company/meat-orders/', company_meat_orders, name='company_meat_orders'),
    path('orders/update-cart/', update_cart, name='update_cart'),
]
