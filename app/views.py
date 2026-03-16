from decimal import Decimal
from django.db import transaction
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render,redirect
from django.http import HttpResponse,JsonResponse
from .models import *
import json
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import make_aware, localtime  
from urllib.parse import urlencode
from django.views.decorators.csrf import csrf_exempt
from .vnpay import vnpay
from datetime import datetime
from .forms import ShippingAddressForm

from django.contrib.admin.views.decorators import staff_member_required

from datetime import datetime, timedelta, time
from django.db.models import Sum


import hmac
import hashlib
import uuid

# Create your views here.
def demosanpham(request,product_id):
    sanpham = get_object_or_404(Product, id=product_id)

    return render(request,'app/sanphamdemo.html',{'sanpham':sanpham})

def thong_tin_thay_co(request):
    thong_tin = Thongtingiaovien.objects.last()
    if request.method == 'POST':
        name = request.POST.get('ten')
        chuyen_nganh = request.POST.get('chuyen_nganh')
        tuoi = request.POST.get('tuoi')
        status = request.POST.get('status') == 'true'

        thongtingiaovien = Thongtingiaovien(name = name, chuyennganh=chuyen_nganh,tuoi=tuoi,status=status)
        thongtingiaovien.save()

    
    if thong_tin.status == 'true':
        trang_thai = 'Đang rảnh '
    else:
        trang_thai = 'Đang bận'


    context ={
        'trang_thai':trang_thai,
        'thong_tin':thong_tin,
        
    }
    return render(request,'app/thong_tin_thay_co.html',context)


# hien thi doanh thu
def thong_ke_doanh_thu(request):
    filter_type = request.GET.get('filter_type', 'day')
    selected_date_str = request.GET.get('date')

    if selected_date_str:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    else:
        selected_date = timezone.localdate()

    queryset = Order.objects.all()
    labels = []
    data = []
    bang_chi_tiet = []

    if filter_type == 'day':
        start_datetime = make_aware(datetime.combine(selected_date, time.min))
        end_datetime = make_aware(datetime.combine(selected_date, time.max))
        queryset = queryset.filter(created_at__range=(start_datetime, end_datetime))
        doanh_thu = queryset.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        labels = [selected_date.strftime('%d/%m/%Y')]
        data = [doanh_thu]
        bang_chi_tiet = [{'thoi_gian': selected_date.strftime('%d/%m/%Y'), 'doanh_thu': doanh_thu}]

    elif filter_type == 'week':
        start = selected_date - timedelta(days=selected_date.weekday())
        for i in range(7):
            day = start + timedelta(days=i)
            start_datetime = make_aware(datetime.combine(day, time.min))
            end_datetime = make_aware(datetime.combine(day, time.max))
            daily_total = Order.objects.filter(created_at__range=(start_datetime, end_datetime)) \
                                       .aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            labels.append(day.strftime('%a %d/%m'))
            data.append(daily_total)
            bang_chi_tiet.append({'thoi_gian': day.strftime('%A, %d/%m'), 'doanh_thu': daily_total})
        doanh_thu = sum(data)

    elif filter_type == 'month':
        year = selected_date.year
        month = selected_date.month
        for day in range(1, 32):
            try:
                d = make_aware(datetime(year, month, day))
                start_datetime = make_aware(datetime.combine(d.date(), time.min))
                end_datetime = make_aware(datetime.combine(d.date(), time.max))
                daily_total = Order.objects.filter(created_at__range=(start_datetime, end_datetime)) \
                                           .aggregate(Sum('total_amount'))['total_amount__sum'] or 0
                labels.append(d.strftime('%d/%m'))
                data.append(daily_total)
                bang_chi_tiet.append({'thoi_gian': d.strftime('%d/%m'), 'doanh_thu': daily_total})
            except ValueError:
                break
        doanh_thu = sum(data)

    elif filter_type == 'year':
        year = selected_date.year
        for month in range(1, 13):
            try:
                month_start = make_aware(datetime(year, month, 1))
                if month == 12:
                    next_month = make_aware(datetime(year + 1, 1, 1))
                else:
                    next_month = make_aware(datetime(year, month + 1, 1))

                monthly_total = Order.objects.filter(
                    created_at__gte=month_start,
                    created_at__lt=next_month
                ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

                labels.append(month_start.strftime('%b'))
                data.append(monthly_total)
                bang_chi_tiet.append({'thoi_gian': month_start.strftime('%B'), 'doanh_thu': monthly_total})
            except Exception as e:
                continue
        doanh_thu = sum(data)

    context = {
        'title': 'Thống kê doanh thu',
        'filter_type': filter_type,
        'selected_date': selected_date.strftime('%Y-%m-%d'),
        'doanh_thu': doanh_thu,
        'labels': labels,
        'data': data,
        'bang_chi_tiet': bang_chi_tiet,
    }

    return render(request, 'admin/custom_admin/thong_ke.html', context)
# trang thanh toan
def order(request):
    categories = Category.objects.filter(is_sub=False)
    if request.user.is_authenticated:
        customer = request.user
        orders = Order.objects.filter(customer=customer).exclude(status='PENDING')
    else:
        orders = []
    

    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer = customer,status = 'PENDING')
        items = order.order_item_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login ="show"
    else:
        items = []
        order = {'get_cart_items':0,'get_cart_total':0 }
        cartItems = order['get_cart_items']
        user_not_login = "show"
        user_login ="hidden"
    return render(request,'app/order.html',{'items':items,'cartItems':cartItems,'user_not_login':user_not_login,'user_login':user_login,'categories':categories, 'orders': orders})

#dang nhap va dang ky
def detail(request, product_id):
    categories = Category.objects.filter(is_sub=False)
    product = get_object_or_404(Product, id=product_id)
    color_ids = product.variants.values_list('color_id', flat=True).distinct()
    

    color_list = Color.objects.filter(id__in=color_ids)
    all_sizes = Size.objects.all()
    if request.user.is_authenticated:
        customer = request.user
       
        order, created = Order.objects.get_or_create(customer = customer,status = 'PENDING')
        items = order.order_item_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login ="show"
    else:
        items = []
        order = {'get_cart_items':0,'get_cart_total':0 }
        cartItems = order['get_cart_items']
        user_not_login = "show"
        user_login ="hidden"
    return render(request,'app/detail.html',{'color_list':color_list,'all_sizes':all_sizes, 'product':product, 'categories':categories,'user_not_login':user_not_login,'user_login':user_login,'product':product,'items': items,'order':order,'cartItems':cartItems})

def category(request):
    categories = Category.objects.filter(is_sub=False)
    active_category = request.GET.get('category','')
    if active_category:
        products = Product.objects.filter(category__slug=active_category)
        
        for product in products:
            variants = product.variants.all()
            size_map = { v.size.name: v.size.id for v in variants if v.size }
            product.size_S  = size_map.get('S')
            product.size_M  = size_map.get('M')
            product.size_L  = size_map.get('L')
            product.size_XL = size_map.get('XL')

            colors_qs = product.variants.values('color__name', 'color__id', 'color__code').distinct()
            color_list = []
            for color in colors_qs:
                has_stock = product.variants.filter(color_id=color['color__id'], stock__gt=0).exists()
                color_list.append({
                    'name': color['color__name'],
                    'id': color['color__id'],
                    'code': color['color__code'],
                    'has_stock': has_stock
                })
            product.color_list = color_list

    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer = customer,status = 'PENDING')
        items = order.order_item_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login ="show"
    else:
        items = []
        order = {'get_cart_items':0,'get_cart_total':0 }
        cartItems = order['get_cart_items']
        user_not_login = "show"
        user_login ="hidden"
    return render(request,'app/category.html',{'products':products,'cartItems':cartItems,'categories':categories,'active_category':active_category,'products':products,'user_not_login':user_not_login,'user_login':user_login})

def search(request):
    searched = ""
    keys = Product.objects.none()
    if request.method == "POST":
        searched = request.POST["searched"]
        keys = Product.objects.filter(name__icontains = searched)

        for product in keys:
            variants = product.variants.all()
            size_map = { v.size.name: v.size.id for v in variants if v.size }
            product.size_S  = size_map.get('S')
            product.size_M  = size_map.get('M')
            product.size_L  = size_map.get('L')
            product.size_XL = size_map.get('XL')

            colors_qs = product.variants.values('color__name', 'color__id', 'color__code').distinct()
            color_list = []
            for color in colors_qs:
                has_stock = product.variants.filter(color_id=color['color__id'], stock__gt=0).exists()
                color_list.append({
                    'name': color['color__name'],
                    'id': color['color__id'],
                    'code': color['color__code'],
                    'has_stock': has_stock
                })
            product.color_list = color_list

    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer = customer,status = 'PENDING')
        items = order.order_item_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login ="show"
    else:
        items = []
        order = {'get_cart_items':0,'get_cart_total':0 }
        cartItems = order['get_cart_items']
        user_not_login = "show"
        user_login ="hidden"
    products = Product.objects.all()
    categories = Category.objects.filter(is_sub=False)
    return render(request,'app/search.html',{"searched":searched,"keys":keys,'products':products,'cartItems':cartItems,'user_not_login':user_not_login,'user_login':user_login,'categories':categories})

def register(request):
    form = CreateUserForm()
    
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        user_not_login = "hidden"
        user_login ="show"
    else:
        user_not_login = "show"
        user_login ="hidden"
            
    return render(request,'app/register.html',{'form':form,'user_not_login':user_not_login,'user_login':user_login})

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username = username, password = password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else: messages.info(request,'tài khoản hoặc mật khẩu không chính xác')
        user_not_login = "hidden"
        user_login ="show"
    else:
        user_not_login = "show"
        user_login ="hidden"

    return render(request,'app/login.html',{'user_not_login':user_not_login,'user_login':user_login})

def logoutPage(request):
    logout(request)
    return redirect('login')

#trang chu
def home(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer = customer,status = 'PENDING')
        items = order.order_item_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login ="show"
    else:
        items = []
        order = {'get_cart_items':0,'get_cart_total':0 }
        cartItems = order['get_cart_items']
        user_not_login = "show"
        user_login ="hidden"
    categories = Category.objects.filter(is_sub=False)
    active_category = request.GET.get('category','')
    
    #tat ca san pham
    products_all = Product.objects.all().order_by('-created_at')
    paginator_all = Paginator(products_all,16)
    page_number_all = request.GET.get('page_all')
    page_obj_all = paginator_all.get_page(page_number_all)
    num_current_all = len(page_obj_all.object_list)
    num_empty_all = paginator_all.per_page - num_current_all
    blanks_all = "x" * num_empty_all

    # Thêm size cho toàn bộ sản phẩm
    for product in page_obj_all:
        variants = product.variants.all()
        size_map = { v.size.name: v.size.id for v in variants if v.size }
        product.size_S  = size_map.get('S')
        product.size_M  = size_map.get('M')
        product.size_L  = size_map.get('L')
        product.size_XL = size_map.get('XL')

        colors_qs = product.variants.values('color__name', 'color__id', 'color__code').distinct()
        color_list = []
        for color in colors_qs:
            has_stock = product.variants.filter(color_id=color['color__id'], stock__gt=0).exists()
            color_list.append({
                'name': color['color__name'],
                'id': color['color__id'],
                'code': color['color__code'],
                'has_stock': has_stock
            })
        product.color_list = color_list
        
    # phan trang cua hang new
    products_new = Product.objects.filter(category__slug="hang-moi").order_by('-created_at')
    paginator_new = Paginator(products_new,8)
    page_number_new = request.GET.get('page_new')
    page_obj_new = paginator_new.get_page(page_number_new)
    num_current_new = len(page_obj_new.object_list)
    num_empty_new   = paginator_new.per_page - num_current_new
    blanks_new = "x" * num_empty_new
    # tao size hang new
    for product in page_obj_new:
        variants = product.variants.all()
        size_map = { v.size.name: v.size.id for v in variants if v.size }
        product.size_S  = size_map.get('S')
        product.size_M  = size_map.get('M')
        product.size_L  = size_map.get('L')
        product.size_XL = size_map.get('XL')

        colors_qs = product.variants.values('color__name', 'color__id', 'color__code').distinct()
        color_list = []
        for color in colors_qs:
            has_stock = product.variants.filter(color_id=color['color__id'], stock__gt=0).exists()
            color_list.append({
                'name': color['color__name'],
                'id': color['color__id'],
                'code': color['color__code'],
                'has_stock': has_stock
            })
        product.color_list = color_list

    # phan trang cua hang 2024
    products_2024 = Product.objects.filter(category__slug="Hang-2025").order_by('-created_at')
    paginator_2024 = Paginator(products_2024,8)
    page_number_2024 = request.GET.get('page_2024')
    page_obj_2024 = paginator_2024.get_page(page_number_2024)
    num_current_2024 = len(page_obj_2024.object_list)
    num_empty_2024 = paginator_2024.per_page - num_current_2024
    blanks_2024 = "x" * num_empty_2024
    # tao size cho hang 20024
    for product in page_obj_2024:
        variants = product.variants.all()
        size_map = { v.size.name: v.size.id for v in variants if v.size }
        product.size_S  = size_map.get('S')
        product.size_M  = size_map.get('M')
        product.size_L  = size_map.get('L')
        product.size_XL = size_map.get('XL')

        colors_qs = product.variants.values('color__name', 'color__id', 'color__code').distinct()
        color_list = []
        for color in colors_qs:
            has_stock = product.variants.filter(color_id=color['color__id'], stock__gt=0).exists()
            color_list.append({
                'name': color['color__name'],
                'id': color['color__id'],
                'code': color['color__code'],
                'has_stock': has_stock
            })
        product.color_list = color_list
    return render(request,'app/home.html', { 'blanks_all':blanks_all, 'page_obj_all':page_obj_all, 'products_all':products_all, 'products_2024':products_2024,'page_obj_2024':page_obj_2024,'blanks_2024':blanks_2024,'blanks_new':blanks_new,'page_obj_new':page_obj_new,'products_new':products_new,'cartItems':cartItems,'user_not_login':user_not_login,'user_login':user_login,'categories':categories,'active_category':active_category,})

def cart(request):
    categories = Category.objects.filter(is_sub=False)

    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer = customer,status = 'PENDING')
        items = order.order_item_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login ="show"
    else:
        items = []
        order = {'get_cart_items':0,'get_cart_total':0 }
        cartItems = order['get_cart_items']
        user_not_login = "show"
        user_login ="hidden"
    
    return render(request,'app/cart.html',{'items': items,'order':order,'cartItems':cartItems,'user_not_login':user_not_login,'user_login':user_login,'categories':categories})

def checkout(request):
    user = request.user
    order, _ = Order.objects.get_or_create(customer=user, status='PENDING')
    last_address = ShippingAddress.objects.filter(customer=user).order_by('-date_added').first()
    shipping_fee = Decimal(40000)

    # 1. Xử lý chọn sản phẩm (POST selected_products)
    if request.method == 'POST' and 'selected_products' in request.POST:
        selected_ids = [int(pid) for pid in request.POST.getlist('selected_products')]
        quantities = {pid: int(request.POST.get(f'quantity_{pid}', 1)) for pid in selected_ids}
        products = Product.objects.filter(id__in=selected_ids)

        # Cập nhật Order_item
        order.order_item_set.exclude(product_id__in=selected_ids).delete()
        for pid in selected_ids:
            quantity = quantities.get(pid, 1)
            oi, _ = Order_item.objects.get_or_create(order=order, product_id=pid)
            oi.quantity = quantity
            oi.save()

        order.shipping_fee = int(shipping_fee)
        order.total_amount = order.get_cart_totalall
        order.save()
        messages.success(request, "Đã cập nhật giỏ hàng.")

    # 2. Xử lý xác nhận thanh toán
    elif request.method == 'POST' and 'address' in request.POST:
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        phone = request.POST.get('phone', '').strip()
        payment_method = request.POST.get('payment_method')

        # Cập nhật địa chỉ
        if last_address:
            last_address.address = address
            last_address.city = city
            last_address.phone = phone
            last_address.save()
        else:
            last_address = ShippingAddress.objects.create(
                customer=user, address=address, city=city, phone=phone
            )

        # Tính lại tổng tiền
        order.shipping_fee = int(shipping_fee)
        order.total_amount = order.get_cart_total + Decimal(shipping_fee)
        order.shipping_address = last_address
        order.payment_method = payment_method

        if payment_method == 'COD':
            with transaction.atomic():
                order.status = 'CONFIRMED'
                order.save()

                # Trừ kho
                for item in order.order_item_set.all():
                    try:
                        ps = ProductVariant.objects.get(
                            product=item.product,
                            size=item.size,
                            color=item.color
                        )
                        old_stock = ps.stock
                        ps.stock = max(ps.stock - item.quantity, 0)
                        ps.save()
                        print(f"Updated stock for {ps}: {old_stock} -> {ps.stock}")
                    except ProductVariant.DoesNotExist:
                        print(f"ProductVariant NOT FOUND in checkout: product={item.product.id}, size={item.size.id if item.size else None}, color={item.color.id if item.color else None}")

                admin_user = User.objects.filter(is_superuser=True).first()
                if admin_user:
                    Notification.objects.create(
                        user=admin_user,
                        message=f"Người dùng {request.user.username} vừa đặt đơn hàng #{order.id}",
                        order_id=order.id
                    )

            messages.success(request, "Đặt hàng thành công!")
            return redirect('order')

        elif payment_method == 'ONLINE':
            order.save()
            return redirect(create_vnpay_url(order, request))

    # 3. Trả dữ liệu cho giao diện
    items = order.order_item_set.select_related('product').all()
    total_quantity = sum(item.quantity for item in items)
    total_price = sum((item.product.price or Decimal('0.00')) * item.quantity for item in items)
    total_payable = total_price + Decimal(order.shipping_fee)

    context = {
        'order': order,
        'items': items,
        'total_quantity': total_quantity,
        'total_price': total_price,
        'shipping_fee': order.shipping_fee,
        'total_payable': total_payable,
        'last_address': last_address,
        'user_login': "show" if request.user.is_authenticated else "hidden",
        'user_not_login': "hidden" if request.user.is_authenticated else "show",
    }

    return render(request, 'app/checkout.html', context)

def quick_checkout(request):
    customer = request.user
    last_address = ShippingAddress.objects.filter(customer=request.user).order_by('-date_added').first()

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        size_id = request.POST.get('size')
        quantity = int(request.POST.get('quantity', 1))
        color_id = request.POST.get('color')


        product = get_object_or_404(Product, id=product_id)
        size = get_object_or_404(Size, id=size_id)
        color = get_object_or_404(Color, id=color_id)
        ps = ProductVariant.objects.filter(product=product, size=size, color = color).first()

        if not ps or ps.stock < quantity:
            messages.error(request, "Không đủ tồn kho cho sản phẩm đã chọn.")
            return redirect('product_detail', product_id=product_id)

        # Tạo đơn hàng tạm (chưa lưu DB)
        item = {
            'product': product,
            'size': size,
            'quantity': quantity,
            'product_id': product.id,
            'color':color,
            
        }
        total_price = product.price * quantity
        shipping_fee = Decimal(40000)
        total_payable = total_price + shipping_fee

        if request.POST.get('address'):
            address = request.POST.get('address','').strip()
            city = request.POST.get('city','').strip()
            phone = request.POST.get('phone','').strip()

            if last_address:
                last_address.address = address
                last_address.city = city
                last_address.phone = phone
                last_address.save()
            else:
                ShippingAddress.objects.create(customer=request.user,address=address,city=city,phone=phone)

            # Thanh toán thật 
            order = Order.objects.create(customer=customer, status='CONFIRMED', payment_method=request.POST.get('payment_method'))
            Order_item.objects.create(order=order, product=product, quantity=quantity, size=size , color=color)
            
            ps.stock = max(ps.stock - quantity, 0)
            ps.save()

            messages.success(request, "Đặt hàng thành công (Mua ngay)!")
            return redirect('order')

        return render(request, 'app/checkout.html', {
            'items': [item],
            'total_quantity': quantity,
            'total_price': total_price,
            'shipping_fee': shipping_fee,
            'total_payable': total_payable,
            'last_address': last_address,
            'user_login': "show",
            'user_not_login': "hidden",
        })

    return redirect('order')

def updateItem(request):
    data = json.loads(request.body)
    productId = data.get('productId')
    size_id = data.get('size')
    color_id = data.get('color')
    quantity = int(data.get('qty', 1))
    action = data.get('action')

    customer = request.user
    product = Product.objects.get(id=productId)

    try:
        size = Size.objects.get(id=size_id)
    except Size.DoesNotExist:
        return JsonResponse({'error': 'Size không tồn tại'}, status=400)
    
    try:     
        color = Color.objects.get(id=color_id)
    except Color.DoesNotExist:
        return JsonResponse({'error': 'Màu không tồn tại'}, status=400)

   
    try:
        variant = ProductVariant.objects.get(product=product, size=size, color=color)
    except ProductVariant.DoesNotExist:
        return JsonResponse({'error': 'Không tìm thấy biến thể sản phẩm phù hợp'}, status=400)
    if variant.stock < quantity:
        return JsonResponse({'error': 'Sản phẩm không đủ hàng trong kho'})
    # Lấy đơn hàng đang chờ
    order, created = Order.objects.get_or_create(customer=customer, status='PENDING')

    # Lấy hoặc tạo item trong đơn hàng
    orderitem, created = Order_item.objects.get_or_create(
        order=order,
        product=product,
        size=size,
        color=color
    )

    if action == 'add':
        orderitem.quantity += quantity
    elif action == 'remove':
        orderitem.quantity = max(orderitem.quantity - quantity, 0)
    elif action == 'set':
        orderitem.quantity = max(quantity, 0)

    orderitem.save()

    
    if action == 'delete':
        Order_item.objects.filter(order=order, product=product, size=size,color=color).delete()
        return JsonResponse({'message': 'Xóa thành công'})

   
    updated_cart = {
        'cartItems': order.get_cart_items,
        'totalPrice': order.get_cart_total,
    }

    return JsonResponse(updated_cart, safe=False)

def check_stock(request):
    Product_id = request.GET.get('product_id')
    size_id = request.GET.get('size_id')
    color_id = request.GET.get('color_id')

    try:
        size = Size.objects.get(id=size_id)
        color = Color.objects.get(id=color_id)
        variant = ProductVariant.objects.get(product_id=Product_id, size=size, color=color)
        return JsonResponse({'stock': variant.stock})
    except (Size.DoesNotExist, Color.DoesNotExist, ProductVariant.DoesNotExist):
        return JsonResponse({'stock': 0})
    
def mark_order_delivered(request, order_id):
    try:
        order = Order.objects.get(pk=order_id, customer=request.user)
        if order.status != 'DELIVERED':
            order.status = 'DELIVERED'
            order.save()
            return JsonResponse({'success': True, 'message': 'Đã xác nhận nhận hàng.'})
        else:
            return JsonResponse({'success': False, 'message': 'Đơn hàng đã được giao trước đó.'})
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Không tìm thấy đơn hàng.'})
    
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)

    if order.status in ['DELIVERED', 'CANCELLED']:
        messages.warning(request, "Đơn hàng này không thể huỷ.")
        return redirect('order')

    with transaction.atomic():
        order.status = 'CANCELLED'
        order.save()

        # Cộng lại stock
        for item in order.order_item_set.all():
            try:
                ps = ProductVariant.objects.get(
                    product=item.product,
                    size=item.size,
                    color=item.color
                )
                old_stock = ps.stock
                ps.stock += item.quantity
                ps.save()
                print(f"Restored stock for {ps}: {old_stock} -> {ps.stock}")
            except ProductVariant.DoesNotExist:
                print(f"ProductVariant NOT FOUND when cancel: product={item.product.id}, size={item.size.id if item.size else None}, color={item.color.id if item.color else None}")

    messages.success(request, "Đơn hàng đã được huỷ và kho đã được cập nhật.")
    return redirect('order')

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def create_vnpay_url(order, request):
    vnp = vnpay()
    vnp.requestData['vnp_Version'] = '2.1.0'
    vnp.requestData['vnp_Command'] = 'pay'
    vnp.requestData['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
    vnp.requestData['vnp_Amount'] = Decimal(order.total_amount * 100 ) 
    vnp.requestData['vnp_CurrCode'] = 'VND'
    vnp.requestData['vnp_TxnRef'] = str(order.id)
    vnp.requestData['vnp_OrderInfo'] = f'Thanh toán đơn hàng #{order.id}'
    vnp.requestData['vnp_OrderType'] = 'other'
    vnp.requestData['vnp_Locale'] = 'vn'
    vnp.requestData['vnp_IpAddr'] = get_client_ip(request)
    vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')
    vnp.requestData['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL

    payment_url = vnp.get_payment_url(settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY)
    return payment_url


def payment_return(request):
    inputData = request.GET
    if not inputData:
        return render(request, "payment_return.html", {"result": "Không có dữ liệu phản hồi."})

    vnp = vnpay()
    vnp.responseData = inputData.dict()

    # Lấy dữ liệu
    order_id = inputData.get('vnp_TxnRef')
    amount = int(inputData.get('vnp_Amount', 0)) / 100  # chuyển từ xu về VND
    vnp_TransactionNo = inputData.get('vnp_TransactionNo')
    vnp_ResponseCode = inputData.get('vnp_ResponseCode')
    vnp_PayDate = inputData.get('vnp_PayDate')
    order_desc = inputData.get('vnp_OrderInfo')
    success = (vnp_ResponseCode == '00')

    # Xác minh chữ ký
    if not vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
        return render(request, "payment_return.html", {
            "result": "Sai checksum. Giao dịch không hợp lệ.",
            "order_id": order_id,
            "amount": amount,
            "order_desc": order_desc
        })

    # Lấy order từ database
    order = get_object_or_404(Order, id=order_id, payment_method='ONLINE')

    if success:
        # Nếu đơn hàng chưa được xác nhận, tiến hành xác nhận
        if order.status != 'CONFIRMED':
            with transaction.atomic():
                order.status = 'CONFIRMED'
                order.save()

                # Trừ kho
                for item in order.order_item_set.all():
                    try:
                        ps = ProductVariant.objects.get(
                            product=item.product,
                            size=item.size,
                            color=item.color
                        )
                        old_stock = ps.stock
                        ps.stock = max(ps.stock - item.quantity, 0)
                        ps.save()
                        print(f"Updated stock for {ps}: {old_stock} -> {ps.stock}")
                    except ProductVariant.DoesNotExist:
                        print(f"ProductVariant NOT FOUND: product={item.product.id}, size={item.size.id if item.size else None}, color={item.color.id if item.color else None}")

                admin_user = User.objects.filter(is_superuser=True).first()
                if admin_user:
                    Notification.objects.create(
                        user=admin_user,
                        message=f"Người dùng {order.customer.username} đã thanh toán thành công đơn hàng #{order.id} (VNPAY).",
                        order_id=order.id
                    )

        messages.success(request, f"Thanh toán thành công đơn hàng #{order_id}!")
        result_text = "Giao dịch thành công"
    else:
        order.status = 'FAILED'
        order.save()
        result_text = "Thanh toán thất bại"
    customer = None
    if request.user.is_authenticated:
        customer = request.user
        
        
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login ="show"
    else:
       
        order = {'get_cart_items':0,'get_cart_total':0 }
        cartItems = order['get_cart_items']
        user_not_login = "show"
        user_login ="hidden"

    return render(request, "app/payment_return.html", {
        "cartItems":cartItems,
        "user_not_login":user_not_login,
        "user_login":user_login,
        "customer":customer,
        "result": result_text,
        "order_id": order_id,
        "amount": amount,
        "order_desc": order_desc,
        "vnp_TransactionNo": vnp_TransactionNo,
        "vnp_ResponseCode": vnp_ResponseCode,
        "vnp_PayDate": vnp_PayDate
    })

def infor(request):
    user = request.user
    shipping = ShippingAddress.objects.get(customer=user)
    
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            if shipping:
                # cập nhật địa chỉ cũ
                for field in form.cleaned_data:
                    setattr(shipping, field, form.cleaned_data[field])
                shipping.save()
            else:
                # tạo mới nếu chưa có
                new_address = form.save(commit=False)
                new_address.customer = user
                new_address.save()
            return redirect('profile')
    else:
        form = ShippingAddressForm(instance=shipping)

    if request.user.is_authenticated:
        customer = request.user
        
        
        # cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login ="show"
    else:
       
        
        # cartItems = order['get_cart_items']
        user_not_login = "show"
        user_login ="hidden"


    return render(request,'app/user_profile.html',{
        'user':user,
        'diachi':shipping,
        'customer':customer,
        # 'cartItems':cartItems,
        'user_not_login':user_not_login,
        'user_login':user_login,
        'form':form,
    })