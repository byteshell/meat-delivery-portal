from django.shortcuts import render, get_object_or_404
from .models import Delivery
from orders.models import Order

def track_delivery(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    delivery = get_object_or_404(Delivery, order=order)
    return render(request, 'logistics/track_delivery.html', {'delivery': delivery})
