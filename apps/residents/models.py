from django.db import models
from django.conf import settings  # <--- Cần import settings để lấy User Model
from apps.utils import BaseModel
from apps.buildings.models import Apartment

class Resident(BaseModel):
    RELATIONSHIP_CHOICES = (
        ('OWNER', 'Chủ hộ'),
        ('TENANT', 'Người thuê'),
        ('MEMBER', 'Thành viên gia đình'),
    )

    # --- MỚI THÊM: Liên kết với tài khoản đăng nhập ---
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='resident', # Tên này giúp User gọi ngược lại Resident (user.resident)
        verbose_name="Tài khoản hệ thống"
    )
    # --------------------------------------------------

    full_name = models.CharField(max_length=255, verbose_name="Họ và tên")
    identity_card = models.CharField(max_length=20, unique=True, verbose_name="CCCD/CMND")
    phone_number = models.CharField(max_length=15, verbose_name="Số điện thoại")
    
    # Ảnh giấy tờ (lưu vào folder media/residents/...)
    identity_card_image_front = models.ImageField(upload_to='residents/id_cards/', null=True, blank=True)
    identity_card_image_back = models.ImageField(upload_to='residents/id_cards/', null=True, blank=True)
    
    emergency_phone = models.CharField(max_length=15, null=True, blank=True, verbose_name="SĐT Khẩn cấp")

    # Liên kết Căn hộ (1 Cư dân - 1 Căn hộ tại 1 thời điểm)
    current_apartment = models.ForeignKey(
        Apartment, 
        on_delete=models.PROTECT, # Không cho xóa phòng nếu còn người
        related_name='residents',
        verbose_name="Căn hộ hiện tại"
    )
    
    relationship_type = models.CharField(
        max_length=20, 
        choices=RELATIONSHIP_CHOICES, 
        default='TENANT',
        verbose_name="Vai trò"
    )

    def __str__(self):
        return f"{self.full_name} - {self.current_apartment.apartment_code}"

    class Meta:
        db_table = 'residents'
        verbose_name = 'Cư dân'
        verbose_name_plural = 'Danh sách Cư dân'

class Vehicle(BaseModel):
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE, related_name='vehicles')
    license_plate = models.CharField(max_length=20, verbose_name="Biển số xe")
    vehicle_type = models.CharField(max_length=50, default="Xe máy", verbose_name="Loại xe")

    def __str__(self):
        return f"{self.license_plate} ({self.resident.full_name})"

    class Meta:
        db_table = 'resident_vehicles'
        verbose_name = 'Phương tiện'
        verbose_name_plural = 'Danh sách Phương tiện'