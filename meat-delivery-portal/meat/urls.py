from django.urls import path
from . import views

urlpatterns = [
    path('', views.meat_list, name='meat_list'),
    path('add/', views.add_meat, name='add_meat'),
    path('company/', views.company_dashboard, name='company_dashboard'),
]
