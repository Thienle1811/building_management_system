from django.db import models
from apps.utils import BaseModel
from django.core.exceptions import ValidationError
from apps.buildings.models import Apartment
from apps.residents.models import Resident

# ... (Giữ nguyên các Class ServiceConfig, PriceTier, VehicleType, InternetPackage cũ) ...
# ... (Bạn copy lại phần code Phase 1 vào đây, hoặc chỉ cần dán đoạn code dưới đây vào CUỐI file) ...

class ServiceConfig(BaseModel):
    SERVICE_TYPES = (
        ('ELECTRICITY', 'Điện'),
        ('WATER', 'Nước'),
        ('MANAGEMENT', 'Phí quản lý'),
    )
    CALCULATION_METHODS = (
        ('TIERED', 'Bậc thang (Lũy tiến)'),
        ('FIXED_PER_UNIT', 'Đồng giá theo số tiêu thụ'),
        ('FIXED_PER_MONTH', 'Cố định theo tháng (Theo căn)'),
        ('PER_SQM', 'Theo diện tích (VNĐ/m2)'),
    )
    name = models.CharField(max_length=255, verbose_name="Tên cấu hình")
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES, verbose_name="Loại dịch vụ")
    calculation_method = models.CharField(max_length=20, choices=CALCULATION_METHODS, verbose_name="Cách tính")
    flat_rate = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="Đơn giá cơ bản")
    vat_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Thuế VAT (%)")
    environment_fee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Phí BVMT (%)")
    is_active = models.BooleanField(default=True, verbose_name="Đang áp dụng")
    description = models.TextField(null=True, blank=True, verbose_name="Mô tả")

    def __str__(self):
        return f"{self.name} ({self.get_service_type_display()})"
    class Meta:
        db_table = 'billing_service_configs'
        verbose_name = 'Cấu hình giá dịch vụ'
        verbose_name_plural = 'Cấu hình giá dịch vụ'

class PriceTier(BaseModel):
    config = models.ForeignKey(ServiceConfig, on_delete=models.CASCADE, related_name='tiers')
    tier_level = models.IntegerField(verbose_name="Bậc số")
    min_value = models.IntegerField(verbose_name="Từ số")
    max_value = models.IntegerField(null=True, blank=True, verbose_name="Đến số")
    price = models.DecimalField(max_digits=15, decimal_places=0, verbose_name="Đơn giá")
    class Meta:
        db_table = 'billing_price_tiers'
        ordering = ['tier_level']

class VehicleType(BaseModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    monthly_price = models.DecimalField(max_digits=15, decimal_places=0)
    description = models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'billing_vehicle_types'
        verbose_name = 'Loại phương tiện'
        verbose_name_plural = 'Bảng giá Phương tiện'

class InternetPackage(BaseModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    bandwidth = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=15, decimal_places=0)
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = 'billing_internet_packages'
        verbose_name = 'Gói cước Internet'
        verbose_name_plural = 'Bảng giá Internet'

# --- PHẦN MỚI THÊM CHO PHASE 2 ---
class MeterReading(BaseModel):
    """
    Bảng lưu chỉ số Điện/Nước hàng tháng
    """
    SERVICE_TYPES = (
        ('ELECTRICITY', 'Điện'),
        ('WATER', 'Nước'),
    )
    
    STATUS_CHOICES = (
        ('PENDING', 'Chờ ghi'),       # Vừa được tạo tự động
        ('RECORDED', 'Đã ghi'),       # Bảo vệ đã nhập số
        ('BILLED', 'Đã tính tiền'),   # Đã chốt hóa đơn (không sửa được nữa)
    )

    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='meter_readings', verbose_name="Căn hộ")
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES, verbose_name="Loại dịch vụ")
    
    # Kỳ ghi nhận (Tháng/Năm)
    record_month = models.IntegerField(verbose_name="Tháng")
    record_year = models.IntegerField(verbose_name="Năm")
    
    # Chỉ số
    old_index = models.IntegerField(default=0, verbose_name="Chỉ số cũ")
    new_index = models.IntegerField(null=True, blank=True, verbose_name="Chỉ số mới")
    consumption = models.IntegerField(default=0, verbose_name="Tiêu thụ")
    
    # Minh chứng
    image_evidence = models.ImageField(upload_to='meter_readings/%Y/%m/', null=True, blank=True, verbose_name="Ảnh đồng hồ")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="Trạng thái")
    note = models.TextField(null=True, blank=True, verbose_name="Ghi chú (Bất thường)")

    def save(self, *args, **kwargs):
        # Tự động tính tiêu thụ
        if self.new_index is not None and self.old_index is not None:
            if self.new_index >= self.old_index:
                self.consumption = self.new_index - self.old_index
            else:
                # Trường hợp đồng hồ quay vòng (ít gặp) hoặc nhập sai -> Cần xử lý ở Form/Serializer
                pass 
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_service_type_display()} - {self.apartment.apartment_code} (T{self.record_month}/{self.record_year})"

    class Meta:
        db_table = 'billing_meter_readings'
        unique_together = ('apartment', 'service_type', 'record_month', 'record_year') # Mỗi tháng chỉ có 1 bản ghi cho 1 loại
        verbose_name = 'Chỉ số Điện/Nước'
        verbose_name_plural = 'Quản lý Chỉ số Điện/Nước'

class ServiceConfig(BaseModel):
    SERVICE_TYPES = (
        ('ELECTRICITY', 'Điện'),
        ('WATER', 'Nước'),
        ('MANAGEMENT', 'Phí quản lý'),
    )
    CALCULATION_METHODS = (
        ('TIERED', 'Bậc thang (Lũy tiến)'),
        ('FIXED_PER_UNIT', 'Đồng giá theo số tiêu thụ'),
        ('FIXED_PER_MONTH', 'Cố định theo tháng (Theo căn)'),
        ('PER_SQM', 'Theo diện tích (VNĐ/m2)'),
    )
    name = models.CharField(max_length=255, verbose_name="Tên cấu hình")
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES, verbose_name="Loại dịch vụ")
    calculation_method = models.CharField(max_length=20, choices=CALCULATION_METHODS, verbose_name="Cách tính")
    flat_rate = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="Đơn giá cơ bản")
    vat_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Thuế VAT (%)")
    environment_fee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Phí BVMT (%)")
    is_active = models.BooleanField(default=True, verbose_name="Đang áp dụng")
    description = models.TextField(null=True, blank=True, verbose_name="Mô tả")

    def __str__(self):
        return f"{self.name} ({self.get_service_type_display()})"
    class Meta:
        db_table = 'billing_service_configs'
        verbose_name = 'Cấu hình giá dịch vụ'
        verbose_name_plural = 'Cấu hình giá dịch vụ'

class PriceTier(BaseModel):
    config = models.ForeignKey(ServiceConfig, on_delete=models.CASCADE, related_name='tiers')
    tier_level = models.IntegerField(verbose_name="Bậc số")
    min_value = models.IntegerField(verbose_name="Từ số")
    max_value = models.IntegerField(null=True, blank=True, verbose_name="Đến số")
    price = models.DecimalField(max_digits=15, decimal_places=0, verbose_name="Đơn giá")
    class Meta:
        db_table = 'billing_price_tiers'
        ordering = ['tier_level']

class VehicleType(BaseModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    monthly_price = models.DecimalField(max_digits=15, decimal_places=0)
    description = models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'billing_vehicle_types'
        verbose_name = 'Loại phương tiện'
        verbose_name_plural = 'Bảng giá Phương tiện'

class InternetPackage(BaseModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    bandwidth = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=15, decimal_places=0)
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = 'billing_internet_packages'
        verbose_name = 'Gói cước Internet'
        verbose_name_plural = 'Bảng giá Internet'

class MeterReading(BaseModel):
    SERVICE_TYPES = (('ELECTRICITY', 'Điện'), ('WATER', 'Nước'))
    STATUS_CHOICES = (('PENDING', 'Chờ ghi'), ('RECORDED', 'Đã ghi'), ('BILLED', 'Đã tính tiền'))
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='meter_readings', verbose_name="Căn hộ")
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES, verbose_name="Loại dịch vụ")
    record_month = models.IntegerField(verbose_name="Tháng")
    record_year = models.IntegerField(verbose_name="Năm")
    old_index = models.IntegerField(default=0, verbose_name="Chỉ số cũ")
    new_index = models.IntegerField(null=True, blank=True, verbose_name="Chỉ số mới")
    consumption = models.IntegerField(default=0, verbose_name="Tiêu thụ")
    image_evidence = models.ImageField(upload_to='meter_readings/%Y/%m/', null=True, blank=True, verbose_name="Ảnh đồng hồ")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="Trạng thái")
    note = models.TextField(null=True, blank=True, verbose_name="Ghi chú")

    def save(self, *args, **kwargs):
        if self.new_index is not None and self.old_index is not None:
            if self.new_index >= self.old_index:
                self.consumption = self.new_index - self.old_index
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_service_type_display()} - {self.apartment.apartment_code} (T{self.record_month}/{self.record_year})"
    class Meta:
        db_table = 'billing_meter_readings'
        unique_together = ('apartment', 'service_type', 'record_month', 'record_year')
        verbose_name = 'Chỉ số Điện/Nước'
        verbose_name_plural = 'Quản lý Chỉ số Điện/Nước'

# --- PHẦN MỚI THÊM CỦA PHASE 3 ---
class Invoice(BaseModel):
    STATUS_CHOICES = (
        ('DRAFT', 'Nháp'),
        ('PENDING', 'Chờ thanh toán'),
        ('PAID', 'Đã thanh toán'),
        ('OVERDUE', 'Quá hạn'),
        ('CANCELLED', 'Đã hủy'),
    )
    PAYMENT_METHOD_CHOICES = (('CASH', 'Tiền mặt'), ('BANKING', 'Chuyển khoản'))

    code = models.CharField(max_length=50, unique=True, verbose_name="Mã hóa đơn")
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='invoices', verbose_name="Căn hộ")
    resident = models.ForeignKey(Resident, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Chủ hộ")
    month = models.IntegerField(verbose_name="Kỳ tháng")
    year = models.IntegerField(verbose_name="Kỳ năm")
    total_amount = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="Tổng tiền")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT', verbose_name="Trạng thái")
    due_date = models.DateField(null=True, blank=True, verbose_name="Hạn thanh toán")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    payment_proof = models.ImageField(upload_to='invoices/proofs/%Y/%m/', null=True, blank=True, verbose_name="Ảnh chuyển khoản")
    note = models.TextField(null=True, blank=True, verbose_name="Ghi chú")

    def __str__(self):
        return f"{self.code} - {self.apartment.apartment_code}"

    class Meta:
        db_table = 'billing_invoices'
        unique_together = ('apartment', 'month', 'year')
        ordering = ['-year', '-month', 'apartment']
        verbose_name = 'Hóa đơn'
        verbose_name_plural = 'Quản lý Hóa đơn'

class InvoiceItem(BaseModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=255, verbose_name="Khoản thu")
    amount = models.DecimalField(max_digits=15, decimal_places=0, verbose_name="Số tiền")
    description = models.TextField(null=True, blank=True, verbose_name="Diễn giải")

    class Meta:
        db_table = 'billing_invoice_items'