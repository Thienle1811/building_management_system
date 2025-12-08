from django.contrib import admin
from .models import Notification, NotificationDevice

@admin.register(NotificationDevice)
class NotificationDeviceAdmin(admin.ModelAdmin):
    # Bỏ 'active', thêm 'last_used' để theo dõi lần cuối truy cập
    list_display = ('user', 'expo_push_token', 'platform', 'last_used', 'created_at')
    
    # Tìm kiếm theo user
    search_fields = ('user__username', 'expo_push_token')
    
    # Bỏ 'active' khỏi bộ lọc
    list_filter = ('platform', 'created_at')
    readonly_fields = ('created_at',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    # Sửa 'user' thành 'recipient' cho khớp với Model
    list_display = ('recipient', 'title', 'notification_type', 'is_read', 'is_sent', 'created_at')
    
    list_filter = ('is_read', 'is_sent', 'notification_type', 'created_at')
    
    # Sửa 'user__username' thành 'recipient__username'
    search_fields = ('recipient__username', 'title', 'body')
    readonly_fields = ('created_at',)