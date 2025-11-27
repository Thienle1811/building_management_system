from django.db import models
from apps.utils import BaseModel
from apps.buildings.models import Apartment
from apps.residents.models import Resident
from django.core.exceptions import ValidationError

class Contract(BaseModel):
    # Định nghĩa các lựa chọn cho loại hợp đồng
    TYPE_CHOICES = (
        ('DIRECT', 'Dài hạn - Trực tiếp'),
        ('INDIRECT', 'Gián tiếp (Môi giới/Sub-lease)'),
        ('SHORT_TERM', 'Ngắn hạn'),
    )
    
    # Định nghĩa trạng thái hợp đồng
    STATUS_CHOICES = (
        ('PENDING', 'Chờ duyệt'),
        ('ACTIVE', 'Đang hiệu lực'),
        ('EXPIRED', 'Đã hết hạn'),
        ('TERMINATED', 'Đã thanh lý/Hủy'),
    )

    # Mã hợp đồng (Bắt buộc, không trùng)
    code = models.CharField(max_length=50, unique=True, verbose_name="Mã hợp đồng")
    
    # Liên kết khóa ngoại (Foreign Keys)
    # 1. Căn hộ: Một căn hộ có thể có nhiều hợp đồng theo thời gian (related_name='contracts')
    apartment = models.ForeignKey(
        Apartment, 
        on_delete=models.PROTECT, 
        related_name='contracts', 
        verbose_name="Căn hộ"
    )
    
    # 2. Cư dân: Người đứng tên trên hợp đồng
    resident = models.ForeignKey(
        Resident, 
        on_delete=models.PROTECT, 
        related_name='contracts', 
        verbose_name="Người đứng tên"
    )
    
    # Thông tin chi tiết
    contract_type = models.CharField(
        max_length=20, 
        choices=TYPE_CHOICES, 
        default='DIRECT', 
        verbose_name="Loại hợp đồng"
    )
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='PENDING', 
        verbose_name="Trạng thái"
    )
    
    start_date = models.DateField(verbose_name="Ngày bắt đầu")
    end_date = models.DateField(verbose_name="Ngày kết thúc")
    
    # File đính kèm (Lưu vào thư mục media/contracts/năm/tháng/)
    contract_file = models.FileField(
        upload_to='contracts/%Y/%m/', 
        null=True, 
        blank=True, 
        verbose_name="File hợp đồng (PDF/Ảnh)"
    )
    
    # Tiền cọc (Optional)
    deposit_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=0, 
        default=0, 
        verbose_name="Tiền đặt cọc (VNĐ)"
    )
    
    note = models.TextField(null=True, blank=True, verbose_name="Ghi chú")

    class Meta:
        db_table = 'contracts'
        verbose_name = 'Hợp đồng'
        verbose_name_plural = 'Danh sách Hợp đồng'
        ordering = ['-created_at'] # Hợp đồng mới nhất hiện lên đầu

    def __str__(self):
        return f"HĐ {self.code} - {self.apartment.apartment_code}"
    
    def clean(self):
        """Kiểm tra logic toàn vẹn dữ liệu ở tầng Model"""
        super().clean()
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError({'end_date': "Ngày kết thúc không được nhỏ hơn ngày bắt đầu."})