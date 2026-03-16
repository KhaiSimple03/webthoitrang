from django.contrib import admin
from .models import *



admin.site.site_header = "Quản lý Website123"
admin.site.site_title = "Giao diện admin" 
admin.site.index_title = "Bảng Điều Khiển" 
# Register your models here.

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Size)
admin.site.register(Product_Size)
admin.site.register(Order)
admin.site.register(Order_item)
admin.site.register(Color)
admin.site.register(ProductVariant)
