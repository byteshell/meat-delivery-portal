from django.urls import path
from . import views

urlpatterns = [
    path('track/<int:order_id>/', views.track_delivery, name='track_delivery'),
]
