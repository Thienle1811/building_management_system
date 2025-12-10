from django.db import models
from django.contrib.auth.models import User
from apps.utils import BaseModel
from apps.feedback.models import Feedback

class StaffProfile(BaseModel):
    """Hồ sơ nhân viên (Liên kết với User)"""
    TEAM_CHOICES = (
        ('SECURITY', 'Tổ Bảo Vệ (An ninh, Bãi xe)'),
        ('CLEANING', 'Tổ Vệ Sinh (Điện nước, Rác thải)'),
        ('MAINTENANCE', 'Tổ Kỹ Thuật (Bảo trì)'),
        ('ADMIN', 'Ban Quản Lý (Văn phòng)'),
    )
    STATUS_CHOICES = (
        ('ACTIVE', 'Đang làm việc'),
        ('ON_LEAVE', 'Nghỉ phép'),
        ('RESIGNED', 'Đã nghỉ việc'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    phone = models.CharField(max_length=15, null=True, blank=True, verbose_name="Số điện thoại")
    team = models.CharField(max_length=20, choices=TEAM_CHOICES, default='SECURITY', verbose_name="Thuộc Tổ/Đội")
    avatar = models.ImageField(upload_to='staff_avatars/', null=True, blank=True, verbose_name="Ảnh đại diện")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE', verbose_name="Trạng thái")

    def __str__(self):
        return f"{self.user.username} - {self.get_team_display()}"
        
    class Meta:
        db_table = 'operation_staff_profiles'
        verbose_name = 'Hồ sơ Nhân viên'
        verbose_name_plural = 'Quản lý Hồ sơ Nhân viên'

class ShiftConfig(BaseModel):
    """Cấu hình Ca trực"""
    name = models.CharField(max_length=50, verbose_name="Tên ca trực")
    start_time = models.TimeField(verbose_name="Giờ bắt đầu")
    end_time = models.TimeField(verbose_name="Giờ kết thúc")
    is_active = models.BooleanField(default=True, verbose_name="Đang áp dụng")

    def __str__(self):
        return f"{self.name} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"

    class Meta:
        db_table = 'operation_shift_configs'
        verbose_name = 'Cấu hình Ca trực'
        verbose_name_plural = 'Cấu hình Ca trực'

class StaffRoster(BaseModel):
    """Lịch trực hàng ngày"""
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='rosters')
    shift = models.ForeignKey(ShiftConfig, on_delete=models.CASCADE)
    date = models.DateField(verbose_name="Ngày trực")
    
    def __str__(self):
        return f"{self.date} - {self.staff.user.username} ({self.shift.name})"

    class Meta:
        db_table = 'operation_staff_rosters'
        verbose_name = 'Lịch phân ca'
        verbose_name_plural = 'Quản lý Lịch trực'

class MaintenanceTask(BaseModel):
    STATUS_CHOICES = (
        ('PENDING', 'Chờ tiếp nhận'),
        ('IN_PROGRESS', 'Đang xử lý'),
        ('COMPLETED', 'Đã hoàn thành'),
        ('CANCELLED', 'Đã hủy'),
    )

    code = models.CharField(max_length=20, unique=True, verbose_name="Mã công việc")
    feedback = models.OneToOneField(Feedback, on_delete=models.CASCADE, related_name='maintenance_task', null=True, blank=True)
    staff = models.ForeignKey(StaffProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks', verbose_name="Người thực hiện")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="Trạng thái")
    assigned_at = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian phân công")
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian bắt đầu")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian hoàn thành")
    result_image = models.ImageField(upload_to='tasks/results/', null=True, blank=True, verbose_name="Ảnh kết quả")
    staff_note = models.TextField(null=True, blank=True, verbose_name="Ghi chú nhân viên")

    def save(self, *args, **kwargs):
        if not self.code:
            last_task = MaintenanceTask.objects.all().order_by('id').last()
            if last_task:
                self.code = f'TASK-{last_task.id + 1}'
            else:
                self.code = 'TASK-1'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.feedback.title if self.feedback else 'No Feedback'}"

    class Meta:
        db_table = 'operation_maintenance_tasks'
        verbose_name = 'Công việc bảo trì'
        verbose_name_plural = 'Quản lý Công việc (Tasks)'