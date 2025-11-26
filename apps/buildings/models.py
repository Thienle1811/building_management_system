from django.db import models
from apps.utils import BaseModel

class Building(BaseModel):
    name = models.CharField(max_length=255, verbose_name="Tên tòa nhà")
    address = models.TextField(verbose_name="Địa chỉ")
    total_floors = models.IntegerField(verbose_name="Tổng số tầng")
    
    def __str__(self):
        return self.name

    class Meta:
        db_table = 'buildings'
        verbose_name = 'Tòa nhà'
        verbose_name_plural = 'Danh sách Tòa nhà'

class Apartment(BaseModel):
    STATUS_CHOICES = (
        ('VACANT', 'Đang mở bán/Trống'),
        ('OCCUPIED', 'Đã bán/Đang ở'),
        ('MAINTENANCE', 'Đang bảo trì'),
    )

    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='apartments', verbose_name="Tòa nhà")
    floor_number = models.IntegerField(verbose_name="Tầng số")
    apartment_code = models.CharField(max_length=50, unique=True, verbose_name="Mã căn hộ")
    
    # --- Các trường phục vụ Catalog (MỚI THÊM) ---
    image = models.ImageField(upload_to='buildings/apartments/', null=True, blank=True, verbose_name="Hình ảnh đại diện")
    price = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="Giá bán/thuê (VNĐ)")
    bedrooms = models.IntegerField(default=1, verbose_name="Số phòng ngủ")
    bathrooms = models.IntegerField(default=1, verbose_name="Số nhà vệ sinh")
    direction = models.CharField(max_length=50, blank=True, verbose_name="Hướng nhà")
    # ---------------------------------------------

    area_m2 = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Diện tích (m2)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='VACANT', verbose_name="Trạng thái")
    description = models.TextField(null=True, blank=True, verbose_name="Mô tả chi tiết")

    def __str__(self):
        return f"{self.apartment_code} - {self.building.name}"

    class Meta:
        db_table = 'apartments'
        ordering = ['building', 'floor_number', 'apartment_code']
        verbose_name = 'Căn hộ'
        verbose_name_plural = 'Danh sách Căn hộ'