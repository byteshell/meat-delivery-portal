from django.urls import path
from . import views

urlpatterns = [
    path('track/', views.track_search, name='track_search'),  # Add this line
    path('track/<int:order_id>/', views.track_delivery, name='track_delivery'),
]
