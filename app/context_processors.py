from app.models import Notification



def admin_notifications(request):
    if request.user.is_authenticated and request.path.startswith('/admin/'):
        notifications = Notification.objects.filter(is_read=False).order_by('-created_at')[:5]
        return {
            'admin_notifications': notifications,
            'admin_notifications_count': notifications.count(),
        }
    return {}