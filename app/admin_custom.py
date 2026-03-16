from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from app.models import Notification

from .models import *
from django.contrib import admin



class CustomAdminSite(AdminSite):
    site_header = "Quản lý Website"
    site_title = "Giao diện admin"
    index_title = "Bảng Điều Khiển"

    def each_context(self, request):
        context = super().each_context(request)
        if request.user.is_authenticated:
            # Thêm thông báo chưa đọc
            notifications = Notification.objects.filter(is_read=False).order_by('-created_at')[:5]
            context['admin_notifications'] = notifications
            context['admin_notifications_count'] = notifications.count()
        return context

# Instance để dùng
custom_admin_site = CustomAdminSite(name='custom_admin')


custom_admin_site.register(Product)
custom_admin_site.register(Category)
custom_admin_site.register(Size)
custom_admin_site.register(Product_Size)
custom_admin_site.register(Order)
custom_admin_site.register(Order_item)
custom_admin_site.register(ProductVariant)