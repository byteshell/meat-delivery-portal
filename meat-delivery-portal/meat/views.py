from django.shortcuts import render, redirect
from .models import Meat
from .forms import MeatForm
from django.contrib.auth.decorators import login_required

def meat_list(request):
    meats = Meat.objects.filter(quantity__gt=0)
    return render(request, 'meat/meat_list.html', {'meats': meats})

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
