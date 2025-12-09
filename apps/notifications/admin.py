from django.contrib import admin
from .models import Notification, NotificationRecipient, NotificationDevice

class NotificationRecipientInline(admin.TabularInline):
    """
    Hiển thị danh sách người nhận ngay bên trong trang chi tiết Thông báo
    """
    model = NotificationRecipient
    extra = 0 # Không hiển thị sẵn các dòng trống thừa
    readonly_fields = ('read_at',) # Ngày đọc chỉ để xem, không sửa
    can_delete = False # Không nên xóa người nhận từ đây (trừ khi cần thiết)
    
    # Hiển thị các trường này trong bảng con
    fields = ('recipient', 'is_read', 'read_at')

    def has_add_permission(self, request, obj):
        return False # Chặn thêm thủ công từng người (vì logic thêm là do API xử lý hàng loạt)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    # Cập nhật list_display với các trường mới của Phase 1
    list_display = ('title', 'notification_type', 'priority', 'target_type', 'is_sent', 'created_at')
    
    # Bộ lọc bên phải
    list_filter = ('notification_type', 'priority', 'target_type', 'is_sent', 'created_at')
    
    # Thanh tìm kiếm
    search_fields = ('title', 'content')
    
    # Gắn bảng con vào
    inlines = [NotificationRecipientInline]
    
    # Sắp xếp mặc định
    ordering = ('-created_at',)

@admin.register(NotificationDevice)
class NotificationDeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'platform', 'last_used', 'created_at')
    list_filter = ('platform',)
    search_fields = ('user__username', 'user__full_name', 'expo_push_token')