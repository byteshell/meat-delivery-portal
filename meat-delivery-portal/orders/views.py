from django.shortcuts import render, redirect
from .models import Order, Item
from meat.models import Meat
from django.contrib.auth.decorators import login_required

@login_required
def cart(request):
    cart = request.session.get('cart', {})
    meats = Meat.objects.filter(id__in=cart.keys())
    cart_items = []
    total = 0
    for meat in meats:
        qty = cart[str(meat.id)]
        cart_items.append({'meat': meat, 'quantity': qty, 'subtotal': meat.price * qty})
        total += meat.price * qty
    return render(request, 'orders/cart.html', {'cart_items': cart_items, 'total': total})

@login_required
def add_to_cart(request, meat_id):
    cart = request.session.get('cart', {})
    if request.method == 'POST':
        try:
            qty = int(request.POST.get('quantity', 1))
            if qty < 1:
                qty = 1
        except (ValueError, TypeError):
            qty = 1
        cart[str(meat_id)] = cart.get(str(meat_id), 0) + qty
    else:
        cart[str(meat_id)] = cart.get(str(meat_id), 0) + 1
    request.session['cart'] = cart
    return redirect('cart')

@login_required
def update_cart(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        for key in list(cart.keys()):
            qty = request.POST.get(f'quantity_{key}')
            try:
                qty = int(qty)
                if qty < 1:
                    cart.pop(key)
                else:
                    cart[key] = qty
            except (ValueError, TypeError):
                continue
        request.session['cart'] = cart
    return redirect('cart')

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart')
    if request.method == 'POST':
        lat = request.POST.get('delivery_latitude')
        lng = request.POST.get('delivery_longitude')
        order = Order.objects.create(
            user=request.user,
            delivery_latitude=lat if lat else None,
            delivery_longitude=lng if lng else None
        )
        for meat_id, qty in cart.items():
            meat = Meat.objects.get(id=meat_id)
            if meat.quantity >= qty:
                Item.objects.create(order=order, meat=meat, quantity=qty, price=meat.price)
                meat.quantity -= qty
                meat.save()
        request.session['cart'] = {}
        return render(request, 'orders/checkout.html', {'order': order})
    return render(request, 'orders/checkout_location.html')

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_history.html', {'orders': orders})
