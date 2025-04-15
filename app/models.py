from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# Create your models here.
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','first_name','last_name','password1','password2' ]

class Customer(models.Model):
    user = models.OneToOneField(User,on_delete=models.SET_NULL,null=True,blank=False)
    name = models.CharField(max_length=200,null=True)
    mail = models.EmailField(unique=True)
    phone = models.CharField(max_length=15,null=True,blank=True)
    address = models.TextField(null=True ,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
class Category(models.Model):
    name = models.CharField(max_length=200,null=True,blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,blank=False)
    name = models.CharField(max_length=200,null=True)
    description = models.TextField(null=True,blank=True)
    price = models.FloatField()
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
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True,blank=False)
    size = models.ForeignKey(Size,on_delete=models.SET_NULL,null=True,blank=True)
    stock = models.FloatField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.size.name} ({self.stock} cái)"
    
class Order(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.SET_NULL,null=True,blank=True) 
    status = models.BooleanField(default=False,null=True,blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
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
class Order_item(models.Model):
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True,blank=False)
    order = models.ForeignKey(Order,on_delete=models.SET_NULL,null=True,blank=False)
    customer = models.ForeignKey(Customer,on_delete=models.SET_NULL,null=True,blank=False)
    size = models.ForeignKey(Size,on_delete=models.SET_NULL,null=True,blank=True)
    quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return str(self.id)
    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

