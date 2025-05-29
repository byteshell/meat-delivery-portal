from django.shortcuts import render
from orders.models import Item
from meat.models import Meat
from datetime import timedelta
from collections import defaultdict, OrderedDict
import calendar
from django.utils import timezone
from sklearn.cluster import KMeans
import numpy as np

def get_season(month):
    # Northern hemisphere
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Autumn'

def forecast(request):
    # Season selection from GET param, default to current season
    season_choices = ['Winter', 'Spring', 'Summer', 'Autumn']
    selected_season = request.GET.get('season')
    now = timezone.now()
    current_month = now.month
    current_season = get_season(current_month)
    if selected_season not in season_choices:
        selected_season = current_season

    meats = Meat.objects.all()
    meat_stock = {}
    for meat in meats:
        key = (meat.meat_type, meat.company.company_name)
        meat_stock[key] = meat_stock.get(key, 0) + meat.quantity

    # Group order history by meat type and month
    items = Item.objects.select_related('order', 'meat', 'meat__company')
    monthly_demand = defaultdict(lambda: defaultdict(int))  # {meat_type: {YYYY-MM: qty}}
    for item in items:
        meat_type = item.meat.meat_type
        order_month = item.order.created_at.strftime('%Y-%m')
        monthly_demand[meat_type][order_month] += item.quantity

    # Prepare clustering data and predictions for selected season
    forecasts = []
    for meat_type in sorted(monthly_demand.keys()):
        # Prepare data for clustering: X = [[month_number]], y = [qty]
        month_qty = []
        month_labels = []
        season_months = []
        for ym, qty in monthly_demand[meat_type].items():
            year, month = map(int, ym.split('-'))
            season = get_season(month)
            if season == selected_season:
                month_qty.append([month])
                month_labels.append(qty)
                season_months.append(month)
        # If enough data, use KMeans to cluster months by demand
        predicted_season = 0
        n_clusters = min(4, len(month_qty)) if len(month_qty) >= 2 else 1
        if len(month_qty) >= 2:
            kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
            kmeans.fit(month_qty)
            # Predict for all months in this season, then average
            pred_vals = []
            for m in set(season_months):
                cluster = kmeans.predict([[m]])[0]
                cluster_qty = [month_labels[idx] for idx, label in enumerate(kmeans.labels_) if label == cluster]
                if cluster_qty:
                    pred_vals.append(np.mean(cluster_qty))
            predicted_season = round(np.mean(pred_vals)) if pred_vals else 0
        elif len(month_qty) == 1:
            predicted_season = month_labels[0]
        else:
            predicted_season = 0

        # Show monthly trend for this meat type
        trend = []
        for ym, qty in OrderedDict(sorted(monthly_demand[meat_type].items())).items():
            trend.append({'month': ym, 'ordered': qty})
        # Aggregate current stock for all companies for this meat type
        total_stock = sum(stock for (mt, _), stock in meat_stock.items() if mt == meat_type)
        forecasts.append({
            'meat_type': meat_type,
            'current_stock': total_stock,
            'selected_season': selected_season,
            'predicted_season': predicted_season,
            'trend': trend,
        })

    return render(request, 'ai/forecast.html', {
        'forecasts': forecasts,
        'season_choices': season_choices,
        'selected_season': selected_season,
    })
