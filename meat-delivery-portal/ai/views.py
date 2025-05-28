from django.shortcuts import render
from orders.models import Item
from meat.models import Meat
from datetime import timedelta
from collections import defaultdict
from django.utils import timezone

def forecast(request):
    # Get all currently available meat (by type and company)
    meats = Meat.objects.all()
    meat_stock = {}
    for meat in meats:
        key = (meat.meat_type, meat.company.company_name)
        meat_stock[key] = meat_stock.get(key, 0) + meat.quantity

    # Get order history for the last 30 days
    last_30_days = timezone.now() - timedelta(days=30)
    items = Item.objects.filter(order__created_at__gte=last_30_days)
    demand_counter = defaultdict(int)
    for item in items:
        key = (item.meat.meat_type, item.meat.company.company_name)
        demand_counter[key] += item.quantity

    # Predict demand: average daily demand in last 30 days * 30 (for next 30 days)
    forecasts = []
    for key in meat_stock:
        meat_type, company_name = key
        current_stock = meat_stock[key]
        ordered_last_30 = demand_counter.get(key, 0)
        avg_daily = ordered_last_30 / 30
        predicted_demand = round(avg_daily * 30)
        forecasts.append({
            'meat_type': meat_type,
            'company_name': company_name,
            'current_stock': current_stock,
            'ordered_last_30': ordered_last_30,
            'predicted_demand': predicted_demand
        })

    forecasts.sort(key=lambda x: (x['meat_type'], x['company_name']))
    return render(request, 'ai/forecast.html', {'forecasts': forecasts})
