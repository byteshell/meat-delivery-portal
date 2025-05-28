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
    cart[str(meat_id)] = cart.get(str(meat_id), 0) + 1
    request.session['cart'] = cart
    return redirect('cart')

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart')
    order = Order.objects.create(user=request.user)
    for meat_id, qty in cart.items():
        meat = Meat.objects.get(id=meat_id)
        if meat.quantity >= qty:
            Item.objects.create(order=order, meat=meat, quantity=qty, price=meat.price)
            meat.quantity -= qty
            meat.save()
    request.session['cart'] = {}
    return render(request, 'orders/checkout.html', {'order': order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_history.html', {'orders': orders})
