from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import json
import datetime
from .models import *
from .utils import cookieCart, cartData, guestOrder

from django.contrib.auth.decorators import login_required

# from django.contrib.auth.forms import UserCreationForm

# from .models import CreateUserForm
# from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.models import User, auth

def registerPage(request):

    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        email = request.POST['email']

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username already exists')
                return redirect('registerPage')
            elif User.objects.filter(email=email).exists():
               messages.info(request, 'email already exists')
               return redirect('registerPage')

            else:
                user = User.objects.create_user(username=username, password=password1, first_name=first_name, last_name=last_name, email=email)
                user.save()
                c = Customer.objects.create(user=user, name=username, email=email)
                c.save()
                
                print('user created')
                return redirect('loginPage')
        else:
            messages.info(request, 'password must match')
            return redirect('registerPage')

    else:
        return render(request, 'store/register.html')

def loginPage(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            username = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, "User Name or Password does not exists")
            return redirect('loginPage')
    else:
        return render(request, 'store/login.html')

def logoutUser(request):
    logout(request)
    return redirect('/')

def store(request):

    data = cartData(request)

    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems, 'shipping':False}
    return render(request, 'store/store.html', context)

@login_required(login_url="loginPage")
def cart(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems, 'shipping':False}
    return render(request, 'store/cart.html', context)
    
@login_required(login_url="loginPage") # redirect to login page ('/login')
def checkout(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    
    context = {'items': items, 'order': order, 'cartItems': cartItems, 'shipping':False}
    return render(request, 'store/checkout.html', context)

def updateItem(request):

    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False,)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    
    orderItem.save()

    if(orderItem.quantity <= 0):
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

# @csrf_exempt
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()

    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        data = json.loads(request.body)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)


    else:
        print('User is not logged in')
        print('COOKIES:', request.COOKIES)

        customer, order = guestOrder(request, data)
        

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode']
        )

    return JsonResponse('Payment complete!', safe=False)