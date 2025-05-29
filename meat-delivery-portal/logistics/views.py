from django.shortcuts import render, get_object_or_404
from .models import Delivery
from orders.models import Order
from django.http import HttpResponseRedirect
from django.urls import reverse

def track_delivery(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    # Collect all unique companies in the order
    companies = []
    seen_company_ids = set()
    for item in order.items.all():
        company = item.meat.company
        if company.id not in seen_company_ids:
            companies.append({
                'name': getattr(company, 'company_name', ''),
                'address': getattr(company, 'address', ''),
                'lat': getattr(company, 'latitude', None),
                'lng': getattr(company, 'longitude', None),
            })
            seen_company_ids.add(company.id)
    delivery_lat = order.delivery_latitude
    delivery_lng = order.delivery_longitude

    try:
        delivery = Delivery.objects.get(order=order)
        error = None
    except Delivery.DoesNotExist:
        delivery = None
        error = "Delivery information is not yet available for this order."

    return render(request, 'logistics/track_delivery.html', {
        'delivery': delivery,
        'order': order,
        'companies': companies,
        'delivery_lat': delivery_lat,
        'delivery_lng': delivery_lng,
        'error': error,
    })

def track_search(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        if order_id and order_id.isdigit():
            return HttpResponseRedirect(reverse('track_delivery', args=[order_id]))
    return render(request, 'logistics/track_search.html')
