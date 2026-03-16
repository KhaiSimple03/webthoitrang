from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class Thongtingiaovien(models.Model):
    name = models.CharField(max_length=300,null=True)
    chuyennganh = models.CharField(max_length=10,null=True)
    tuoi = models.IntegerField()
    status = models.BooleanField(default=False)
    

class Color(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10, blank=True,null=True)

    def __str__(self):
        return self.name

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    order_id = models.IntegerField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Thông báo đơn hàng #{self.order_id} - {self.user.username}"


# Create your models here.
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','first_name','last_name','password1','password2' ]


class ShippingAddress(models.Model):
    customer = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=False)
    address = models.CharField(max_length=200,null=True)
    city = models.CharField(max_length=100,null=True)
    state = models.CharField(max_length=100,null=True)
    phone = models.CharField(max_length=100,null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.address}, {self.city}"
        
class Category(models.Model):
    sub_category = models.ForeignKey('self',on_delete=models.CASCADE,related_name='sub_categories',null=True,blank=True)
    is_sub =models.BooleanField(default=False)
    name = models.CharField(max_length=200,null=True,blank=True)
    slug = models.SlugField(max_length=200,unique=True)
    image = models.ImageField(null=True,blank=True)

    def __str__(self):
        return self.name
    @property
    def ImageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
    
    
class Product(models.Model):
    category = models.ManyToManyField(Category,related_name='product')
    name = models.CharField(max_length=200,null=True)
    description = models.TextField(null=True,blank=True)
    price = models.PositiveIntegerField()
    image = models.ImageField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    @property
    def ImageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
class Size(models.Model):
    name = models.CharField(max_length=10,unique=True)

    def __str__(self):
        return self.name
    
class Product_Size(models.Model):
    product = models.ForeignKey(Product,related_name='product_sizes',on_delete=models.SET_NULL,null=True,blank=False)
    size = models.ForeignKey(Size,on_delete=models.SET_NULL,null=True,blank=True)
    STATUS_CHOICES = (
        ('in', 'Còn hàng'),
        ('out', 'Hết hàng'),)
    stock = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='in')
    def __str__(self):
        return f"{self.product.name} - {self.size.name} ({self.stock} cái)"
    class Meta:
        unique_together = ('product', 'size')


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='variants',on_delete=models.SET_NULL,null=True)
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True,blank=True)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True,blank=True)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.color.name if self.color else 'No color'} - {self.size.name if self.size else 'No size'} ({self.stock} cái)"

    class Meta:
        unique_together = ('product','color','size')

class Order(models.Model):
    customer = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    shipping_address = models.ForeignKey(ShippingAddress,on_delete=models.SET_NULL,null=True,blank=True)
    payment_choices = [('COD','thanh toán khi nhận hàng'),('ONLINE','thanh toán trực tuyến')]
    payment_method = models.CharField(max_length=10,choices=payment_choices,default='COD')
    status_choices = [('PENDING','Chờ xử lý'),('CONFIRMED','Đã xác nhận'),('PAID','Đã thanh toán'),('DELIVERED','Đã giao'),('CANCELLED','Đã hủy'),]
    status = models.CharField(max_length=20,choices=status_choices, default='PENDING')
    shipping_fee = models.IntegerField(default=0)
    total_amount = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.pk:
            original = Order.objects.get(pk=self.pk)
            if original.status in['CANCELLED', 'DELIVERED' ] and self.status != original.status:
                raise ValueError("Không thể thay đổi trạng thái đơn hàng sau khi đã giao.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Đơn #{self.id} - {self.get_status_display()}"
    @property
    def get_cart_items(self):
        order_items = self.order_item_set.all()
        total = sum([item.quantity for item in order_items])
        return total
    @property
    def get_cart_total(self):
        order_items = self.order_item_set.all()
        total = sum([item.get_total for item in order_items])
        return total
    @property
    def get_cart_totalall(self):
        return self.get_cart_total + Decimal('40000')
class Order_item(models.Model):
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True,blank=False)
    order = models.ForeignKey(Order,on_delete=models.SET_NULL,null=True,blank=False)
    customer = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=False)
    size = models.ForeignKey(Size,on_delete=models.SET_NULL,null=True,blank=True)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return str(self.id)
    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

