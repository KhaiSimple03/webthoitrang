from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from .models import *
import json
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
#dang nhap va dang ky
def register(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            
    return render(request,'app/register.html',{'form':form})

def login(request):
    return render(request,'app/login.html')

#trang chu
def home(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer,status = False)
        items = order.order_item_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_items':0,'get_cart_total':0 }
        cartItems = order['get_cart_items']
    products = Product.objects.all()
    return render(request,'app/home.html', {'products':products,'cartItems':cartItems})
def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer,status = False)
        items = order.order_item_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_items':0,'get_cart_total':0 }
        cartItems = order['get_cart_items']
    
    return render(request,'app/cart.html',{'items': items,'order':order,'cartItems':cartItems})
def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer,status = False)
        items = order.order_item_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_items':0,'get_cart_total':0 }
        cartItems = order['get_cart_items']
    
    return render(request,'app/checkout.html',{'items': items,'order':order,'cartItems':cartItems})
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    customer = request.user.customer
    product = Product.objects.get(id = productId)
    order,created = Order.objects.get_or_create(customer = customer,status = False)
    orderitem,created = Order_item.objects.get_or_create(order = order, product=product)
    if action == 'add':
        orderitem.quantity +=1
    elif action == 'remove':
        orderitem.quantity -=1
    orderitem.save()
    if orderitem.quantity<=0:
        orderitem.delete()

    return JsonResponse('added',safe=False)
