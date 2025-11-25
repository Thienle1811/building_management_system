from django.db import models
from django.utils import timezone

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        # Mặc định chỉ lấy các dòng chưa bị xóa (deleted_at là Null)
        return super().get_queryset().filter(deleted_at__isnull=True)

class BaseModel(models.Model):
    """
    Model cơ sở cho toàn bộ dự án:
    - Tự động lưu thời gian tạo/sửa.
    - Hỗ trợ Soft Delete (Xóa mềm).
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Ngày xóa")

    objects = SoftDeleteManager()      # Manager mặc định (ẩn dòng đã xóa)
    all_objects = models.Manager()     # Manager lấy tất cả (kể cả đã xóa)

    class Meta:
        abstract = True  # Django sẽ không tạo bảng cho model này

    def soft_delete(self):
        """Hàm dùng để xóa mềm"""
        self.deleted_at = timezone.now()
        self.save()