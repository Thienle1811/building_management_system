from django.db import models
from django.conf import settings
from apps.utils import BaseModel
from apps.buildings.models import Apartment

class Resident(BaseModel):
    RELATIONSHIP_CHOICES = (
        ('OWNER', 'Chủ hộ'),
        ('TENANT', 'Người thuê'),
        ('MEMBER', 'Thành viên gia đình'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='resident', 
        verbose_name="Tài khoản hệ thống"
    )

    full_name = models.CharField(max_length=255, verbose_name="Họ và tên")
    identity_card = models.CharField(max_length=20, unique=True, verbose_name="CCCD/CMND")
    phone_number = models.CharField(max_length=15, verbose_name="Số điện thoại")
    
    identity_card_image_front = models.ImageField(upload_to='residents/id_cards/', null=True, blank=True)
    identity_card_image_back = models.ImageField(upload_to='residents/id_cards/', null=True, blank=True)
    
    emergency_phone = models.CharField(max_length=15, null=True, blank=True, verbose_name="SĐT Khẩn cấp")

    current_apartment = models.ForeignKey(
        Apartment, 
        on_delete=models.PROTECT, 
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
    VEHICLE_TYPES = (
        ('CAR', 'Ô tô'),
        ('MOTORBIKE', 'Xe máy'),
        ('BICYCLE', 'Xe đạp'),
        ('OTHER', 'Khác'),
    )
    
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE, related_name='vehicles', verbose_name="Chủ xe")
    license_plate = models.CharField(max_length=20, verbose_name="Biển số xe")
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES, default='MOTORBIKE', verbose_name="Loại xe")
    
    # ===> CÁC TRƯỜNG MỚI BỔ SUNG ĐỂ SỬA LỖI <===
    manufacturer = models.CharField(max_length=50, null=True, blank=True, verbose_name="Hãng sản xuất")
    model = models.CharField(max_length=50, null=True, blank=True, verbose_name="Dòng xe")
    color = models.CharField(max_length=20, null=True, blank=True, verbose_name="Màu sắc")

    def __str__(self):
        return f"{self.license_plate} ({self.resident.full_name})"

    class Meta:
        db_table = 'resident_vehicles'
        verbose_name = 'Phương tiện'
        verbose_name_plural = 'Danh sách Phương tiện'