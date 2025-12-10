from django.db import models
from django.contrib.auth import get_user_model
from apps.utils import BaseModel
from django.core.exceptions import ValidationError

User = get_user_model()

class StaffProfile(BaseModel):
    """Hồ sơ nhân viên vận hành (Bảo vệ / Vệ sinh)"""
    TEAM_CHOICES = (
        ('SECURITY', 'Tổ Bảo Vệ (An ninh, Bãi xe)'),
        ('CLEANING', 'Tổ Vệ Sinh (Điện nước, Rác thải)'),
        ('MAINTENANCE', 'Tổ Kỹ Thuật (Bảo trì)'),
    )
    STATUS_CHOICES = (
        ('ACTIVE', 'Đang làm việc'),
        ('ON_LEAVE', 'Đang nghỉ phép'),
        ('RESIGNED', 'Đã nghỉ việc'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile', verbose_name="Tài khoản hệ thống")
    team = models.CharField(max_length=20, choices=TEAM_CHOICES, verbose_name="Thuộc Tổ/Đội")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE', verbose_name="Trạng thái")
    
    phone_number = models.CharField(max_length=15, verbose_name="Số điện thoại", null=True, blank=True)
    citizen_id = models.CharField(max_length=20, verbose_name="CCCD/CMND", unique=True, null=True, blank=True)
    avatar = models.ImageField(upload_to='staff_avatars/', null=True, blank=True, verbose_name="Ảnh đại diện")
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.get_team_display()}"

    class Meta:
        db_table = 'operation_staff_profiles'
        verbose_name = 'Hồ sơ Nhân viên'
        verbose_name_plural = 'Quản lý Hồ sơ Nhân viên'

class ShiftConfig(BaseModel):
    """Cấu hình khung giờ các ca trực"""
    name = models.CharField(max_length=50, verbose_name="Tên ca (VD: Ca Sáng)")
    start_time = models.TimeField(verbose_name="Giờ bắt đầu")
    end_time = models.TimeField(verbose_name="Giờ kết thúc")
    color_code = models.CharField(max_length=7, default='#3788d8', verbose_name="Màu hiển thị (Hex)")
    is_active = models.BooleanField(default=True, verbose_name="Đang sử dụng")

    def __str__(self):
        return f"{self.name} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"

    class Meta:
        db_table = 'operation_shift_configs'
        verbose_name = 'Cấu hình Ca trực'
        verbose_name_plural = 'Cấu hình Ca trực'
        ordering = ['start_time']

class StaffRoster(BaseModel):
    """Bảng phân công ca trực (Lịch làm việc)"""
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='rosters', verbose_name="Nhân viên")
    shift = models.ForeignKey(ShiftConfig, on_delete=models.CASCADE, verbose_name="Ca trực")
    date = models.DateField(verbose_name="Ngày trực")
    note = models.CharField(max_length=255, null=True, blank=True, verbose_name="Ghi chú")

    def clean(self):
        # Validate: Kiểm tra xem nhân viên này đã có ca trực trùng trong ngày chưa
        # (Logic đơn giản: 1 người không làm 2 ca giống nhau trong 1 ngày)
        if StaffRoster.objects.filter(staff=self.staff, date=self.date, shift=self.shift).exclude(pk=self.pk).exists():
            raise ValidationError("Nhân viên này đã được xếp ca trực này trong ngày rồi.")

    def __str__(self):
        return f"{self.date}: {self.staff} - {self.shift.name}"

    class Meta:
        db_table = 'operation_staff_rosters'
        verbose_name = 'Lịch phân ca'
        verbose_name_plural = 'Quản lý Lịch trực'
        unique_together = ('staff', 'shift', 'date') # Ràng buộc DB: 1 người, 1 ca, 1 ngày chỉ có 1 dòng
        ordering = ['-date', 'shift__start_time']

from apps.feedback.models import Feedback # Import Feedback từ module cũ

class MaintenanceTask(BaseModel):
    """Công việc bảo trì/xử lý sự cố gán cho nhân viên"""
    STATUS_CHOICES = (
        ('PENDING', 'Chờ tiếp nhận'),   # Chưa ai nhận hoặc chưa gán được
        ('IN_PROGRESS', 'Đang xử lý'),  # Nhân viên đã bấm nhận
        ('COMPLETED', 'Đã hoàn thành'), # Đã làm xong & Chụp ảnh
        ('CANCELLED', 'Đã hủy'),
    )

    code = models.CharField(max_length=20, unique=True, verbose_name="Mã công việc")
    feedback = models.OneToOneField(Feedback, on_delete=models.CASCADE, related_name='maintenance_task', verbose_name="Phản hồi gốc")
    staff = models.ForeignKey(StaffProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks', verbose_name="Người thực hiện")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="Trạng thái")
    assigned_at = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian phân công")
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian bắt đầu")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian hoàn thành")
    
    result_image = models.ImageField(upload_to='tasks/results/%Y/%m/', null=True, blank=True, verbose_name="Ảnh kết quả")
    staff_note = models.TextField(null=True, blank=True, verbose_name="Ghi chú của NV")

    def save(self, *args, **kwargs):
        if not self.code:
            # Tự sinh mã task: T-ID_Feedback (VD: T-102)
            self.code = f"TASK-{self.feedback.id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.get_status_display()}"

    class Meta:
        db_table = 'operation_maintenance_tasks'
        verbose_name = 'Công việc bảo trì'
        verbose_name_plural = 'Quản lý Công việc (Tasks)'