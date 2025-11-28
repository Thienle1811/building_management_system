from django.db import models
from django.conf import settings
from apps.utils import BaseModel

class Notification(BaseModel):
    TYPE_CHOICES = (
        ('FEEDBACK_UPDATE', 'Cập nhật phản hồi'),
        ('SYSTEM', 'Thông báo hệ thống'),
    )

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications', verbose_name="Người nhận")
    title = models.CharField(max_length=255, verbose_name="Tiêu đề")
    body = models.TextField(verbose_name="Nội dung")
    notification_type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='SYSTEM')
    
    # Metadata để Deep-link (Mở app đúng chỗ)
    reference_id = models.CharField(max_length=50, null=True, blank=True, verbose_name="ID tham chiếu (VD: Mã FB)")
    
    # Trạng thái gửi
    is_sent = models.BooleanField(default=False, verbose_name="Đã gửi")
    scheduled_at = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian dự kiến gửi")
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian thực gửi")

    def __str__(self):
        return f"[{self.get_notification_type_display()}] {self.title} -> {self.recipient.username}"

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        verbose_name = 'Thông báo'
        verbose_name_plural = 'Danh sách thông báo'