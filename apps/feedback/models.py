import os
from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from apps.utils import BaseModel
from apps.buildings.models import Apartment
from apps.residents.models import Resident

# --- VALIDATOR ---
def validate_file_size(value):
    limit = 20 * 1024 * 1024  # 20MB
    if value.size > limit:
        raise ValidationError('File đính kèm không được vượt quá 20MB.')

class FeedbackCategory(BaseModel):
    """Danh mục phản hồi (Điện, Nước, An ninh...)"""
    name = models.CharField(max_length=100, verbose_name="Tên danh mục")
    code = models.CharField(max_length=50, unique=True, verbose_name="Mã danh mục")
    description = models.TextField(null=True, blank=True, verbose_name="Mô tả")
    
    # --- MỚI THÊM ---
    is_default = models.BooleanField(default=False, verbose_name="Là mặc định")
    is_deletable = models.BooleanField(default=True, verbose_name="Có thể xóa")
    
    def __str__(self):
        return self.name

    class Meta:
        db_table = 'feedback_categories'
        verbose_name = 'Danh mục phản hồi'
        verbose_name_plural = 'Danh mục phản hồi'

class Feedback(BaseModel):
    STATUS_CHOICES = (
        ('PENDING', 'Chờ tiếp nhận'),
        ('PROCESSING', 'Đang xử lý'),
        ('DONE', 'Đã hoàn thành'),
        ('CANCELLED', 'Đã hủy'),
    )
    
    PRIORITY_CHOICES = (
        ('LOW', 'Thấp'),
        ('NORMAL', 'Bình thường'),
        ('HIGH', 'Cao'),
        ('URGENT', 'Khẩn cấp'),
    )

    SOURCE_CHOICES = (
        ('MOBILE', 'Mobile App'),
        ('WEB', 'Web Portal'),
        ('DIRECT', 'Trực tiếp/Hotline'),
    )

    # Định danh
    code = models.CharField(max_length=50, unique=True, editable=False, verbose_name="Mã phản hồi")
    
    # Quan hệ
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='feedbacks', verbose_name="Căn hộ")
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE, related_name='feedbacks', verbose_name="Người gửi")
    category = models.ForeignKey(FeedbackCategory, on_delete=models.PROTECT, related_name='feedbacks', verbose_name="Danh mục")
    
    # Nội dung
    title = models.CharField(max_length=255, verbose_name="Tiêu đề")
    description = models.TextField(verbose_name="Nội dung chi tiết")
    
    # Trạng thái & Phân loại
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="Trạng thái")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='NORMAL', verbose_name="Mức độ ưu tiên")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='MOBILE', verbose_name="Nguồn")
    
    # Xử lý
    internal_note = models.TextField(null=True, blank=True, verbose_name="Ghi chú nội bộ BQL")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian hoàn thành")

    def save(self, *args, **kwargs):
        # Tự động sinh mã FB nếu chưa có
        if not self.code:
            import datetime
            import random
            now = datetime.datetime.now()
            # Format: FB-YYYYMMDD-XXXX (VD: FB-20251128-1234)
            random_str = str(random.randint(1000, 9999))
            self.code = f"FB-{now.strftime('%Y%m%d')}-{random_str}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.status}] {self.title} - {self.code}"

    class Meta:
        db_table = 'feedbacks'
        ordering = ['-created_at']
        verbose_name = 'Phản hồi cư dân'
        verbose_name_plural = 'Danh sách phản hồi'

class FeedbackAttachment(BaseModel):
    """File đính kèm (Ảnh/Video)"""
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='feedback/%Y/%m/', validators=[validate_file_size], verbose_name="File")
    file_type = models.CharField(max_length=50, null=True, blank=True, verbose_name="Loại file") # image/png, video/mp4...
    
    def save(self, *args, **kwargs):
        # Tự động lưu file_type khi upload
        if self.file:
            _, ext = os.path.splitext(self.file.name)
            self.file_type = ext.lower().replace('.', '')
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'feedback_attachments'

class FeedbackStatusHistory(BaseModel):
    """Lịch sử thay đổi trạng thái"""
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=20, choices=Feedback.STATUS_CHOICES, null=True, blank=True)
    new_status = models.CharField(max_length=20, choices=Feedback.STATUS_CHOICES)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Người cập nhật")
    note = models.TextField(null=True, blank=True, verbose_name="Ghi chú thay đổi")

    class Meta:
        db_table = 'feedback_status_history'
        ordering = ['-created_at']