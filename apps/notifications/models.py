from django.db import models
from django.conf import settings
from apps.utils import BaseModel

class Notification(BaseModel):
    # --- CÁC LỰA CHỌN (CHOICES) ---
    PRIORITY_CHOICES = (
        ('NORMAL', 'Thông thường'),
        ('IMPORTANT', 'Quan trọng'),
        ('URGENT', 'Khẩn cấp'),
    )
    
    TYPE_CHOICES = (
        ('SYSTEM', 'Hệ thống'),
        ('FEEDBACK', 'Phản hồi'),
        ('ANNOUNCEMENT', 'Thông báo chung'),
        ('WORK', 'Công việc'), # Dành cho đội vận hành
    )

    TARGET_TYPE_CHOICES = (
        ('ALL_RESIDENTS', 'Toàn bộ cư dân'),
        ('BLOCK', 'Theo tòa nhà'),
        ('FLOOR', 'Theo tầng'),
        ('SPECIFIC_UNITS', 'Danh sách căn hộ cụ thể'),
        ('INTERNAL_GROUP', 'Nhóm nội bộ (Bảo vệ/Vệ sinh...)'),
        ('SPECIFIC_USERS', 'Người dùng cụ thể'),
    )

    # --- THÔNG TIN CƠ BẢN ---
    title = models.CharField(max_length=255, verbose_name="Tiêu đề")
    content = models.TextField(verbose_name="Nội dung")
    
    # Phân loại & Ưu tiên
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='SYSTEM', verbose_name="Loại thông báo")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='NORMAL', verbose_name="Mức độ ưu tiên")
    
    # --- FILE ĐÍNH KÈM (Phase 3 sẽ cấu hình lưu S3, giờ cứ để FileField) ---
    file = models.FileField(upload_to='notifications/%Y/%m/', null=True, blank=True, verbose_name="File đính kèm")

    # --- ĐỊNH TUYẾN NGƯỜI NHẬN (METADATA) ---
    # Các trường này giúp Admin biết tin này đã gửi cho nhóm nào
    target_type = models.CharField(max_length=50, choices=TARGET_TYPE_CHOICES, default='ALL_RESIDENTS', verbose_name="Loại đối tượng")
    # Lưu ID của Block, Tầng, hoặc Group ID (Lưu dạng chuỗi hoặc JSON nếu cần nhiều ID)
    target_identifier = models.CharField(max_length=255, null=True, blank=True, verbose_name="Định danh đối tượng (VD: Block A)")

    # --- TRẠNG THÁI GỬI (Phase 4 Celery sẽ dùng) ---
    scheduled_at = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian dự kiến gửi")
    is_sent = models.BooleanField(default=False, verbose_name="Đã gửi")
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian thực gửi")

    # Metadata cũ (giữ lại nếu cần tham chiếu ngược)
    reference_id = models.CharField(max_length=50, null=True, blank=True, verbose_name="ID tham chiếu (VD: Mã FB)")

    def __str__(self):
        return f"[{self.get_priority_display()}] {self.title}"

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        verbose_name = 'Thông báo'
        verbose_name_plural = 'Danh sách thông báo'


class NotificationRecipient(BaseModel):
    """
    Bảng trung gian lưu trữ trạng thái đọc của từng người nhận.
    Một Notification sẽ sinh ra N dòng trong bảng này.
    """
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='recipients', verbose_name="Thông báo")
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_notifications', verbose_name="Người nhận")
    
    is_read = models.BooleanField(default=False, verbose_name="Đã đọc")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian đọc")

    class Meta:
        db_table = 'notification_recipients'
        unique_together = ('notification', 'recipient') # Một người chỉ nhận 1 bản copy của 1 thông báo
        indexes = [
            models.Index(fields=['recipient', 'is_read']), # Index để query nhanh số tin chưa đọc
        ]
        verbose_name = 'Người nhận thông báo'
        verbose_name_plural = 'Danh sách người nhận'


class NotificationDevice(BaseModel):
    """
    Lưu trữ Expo Push Token của thiết bị người dùng (Giữ nguyên như cũ)
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='devices', verbose_name="Người dùng")
    expo_push_token = models.CharField(max_length=255, unique=True, verbose_name="Expo Token")
    platform = models.CharField(max_length=20, null=True, blank=True, verbose_name="Hệ điều hành (ios/android)")
    last_used = models.DateTimeField(auto_now=True, verbose_name="Lần cuối truy cập")

    def __str__(self):
        return f"{self.user.username} - {self.expo_push_token[:15]}..."

    class Meta:
        db_table = 'notification_devices'
        verbose_name = 'Thiết bị nhận tin'
        verbose_name_plural = 'Danh sách thiết bị'