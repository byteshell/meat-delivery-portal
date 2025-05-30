from django.shortcuts import render, redirect
from .models import Meat
from .forms import MeatForm
from django.contrib.auth.decorators import login_required
from orders.models import Item
from django.core.paginator import Paginator

def home(request):
    # Landing page view
    return render(request, 'meat/home.html')

def meat_list(request):
    meats = Meat.objects.filter(quantity__gt=0)
    meat_types = Meat.MEAT_TYPE_CHOICES
    companies = Meat.objects.values_list('company__id', 'company__company_name').distinct()

    selected_meat_type = request.GET.get('meat_type')
    selected_company = request.GET.get('company')

    if selected_meat_type:
        meats = meats.filter(meat_type=selected_meat_type)
    if selected_company:
        meats = meats.filter(company__id=selected_company)

    # Pagination
    paginator = Paginator(meats, 9)  # 9 meats per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'meat/meat_list.html', {
        'meats': page_obj.object_list,
        'meat_types': meat_types,
        'companies': companies,
        'selected_meat_type': selected_meat_type,
        'selected_company': selected_company,
        'page_obj': page_obj,
    })

@login_required
def add_meat(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'company':
        return redirect('meat_list')
    if request.method == 'POST':
        form = MeatForm(request.POST)
        if form.is_valid():
            meat = form.save(commit=False)
            meat.company = request.user.profile
            meat.save()
            return redirect('company_dashboard')
    else:
        form = MeatForm()
    return render(request, 'meat/add_meat.html', {'form': form})

@login_required
def company_dashboard(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'company':
        return redirect('meat_list')
    meats = Meat.objects.filter(company=request.user.profile)
    return render(request, 'meat/company_dashboard.html', {'meats': meats})

@login_required
def company_meat_orders(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'company':
        return redirect('meat_list')
    meats = Meat.objects.filter(company=request.user.profile)
    # For each meat, get orders and user breakdown
    meat_orders = []
    for meat in meats:
        # Get all items for this meat
        items = Item.objects.filter(meat=meat)
        user_orders = {}
        for item in items:
            username = item.order.user.username
            user_orders[username] = user_orders.get(username, 0) + item.quantity
        meat_orders.append({
            'meat': meat,
            'current_quantity': meat.quantity,
            'user_orders': user_orders
        })
    return render(request, 'meat/company_meat_orders.html', {'meat_orders': meat_orders})
