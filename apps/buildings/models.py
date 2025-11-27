from django.db import models
from apps.utils import BaseModel

class Building(BaseModel):
    name = models.CharField(max_length=255, verbose_name="Tên tòa nhà")
    code = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="Mã tòa nhà")
    address = models.TextField(verbose_name="Địa chỉ")
    total_floors = models.IntegerField(verbose_name="Tổng số tầng")
    
    # Thông tin mở rộng
    description = models.TextField(null=True, blank=True, verbose_name="Mô tả chung")
    total_units = models.IntegerField(default=0, verbose_name="Tổng số căn hộ")
    
    # --- MỚI THÊM: Cấu hình mặc định để sinh tự động ---
    units_per_floor_default = models.IntegerField(default=10, verbose_name="Số căn/tầng mặc định")
    
    def __str__(self):
        return self.name

    def generate_apartments(self):
        """
        Hàm tự động sinh căn hộ (Skeleton)
        Tên căn hộ sẽ theo format: {Mã Tòa}-{Tầng}.{Số Căn} (VD: DIA-05.01)
        """
        apartments_to_create = []
        
        # Duyệt qua từng tầng
        for floor in range(1, self.total_floors + 1):
            # Duyệt qua từng căn trong tầng
            for unit in range(1, self.units_per_floor_default + 1):
                # Format số căn: 01, 02...
                unit_str = f"{unit:02d}"
                
                # Tạo mã căn: CODE-Tầng.Căn (VD: DIA-01.01)
                b_code = self.code if self.code else f"B{self.id}"
                apt_code = f"{b_code}-{floor:02d}.{unit_str}"
                
                # Kiểm tra nếu chưa tồn tại thì thêm vào danh sách tạo
                if not Apartment.objects.filter(apartment_code=apt_code).exists():
                    apartments_to_create.append(Apartment(
                        building=self,
                        floor_number=floor,
                        unit_number=unit_str,
                        apartment_code=apt_code,
                        status='VACANT', # Mặc định là trống
                        net_area=0,      # Để BQL nhập sau
                        room_type='2PN'  # Mặc định
                    ))
        
        # Dùng bulk_create để tạo nhanh 1 lần
        if apartments_to_create:
            Apartment.objects.bulk_create(apartments_to_create)
            return len(apartments_to_create)
        return 0

    class Meta:
        db_table = 'buildings'
        verbose_name = 'Tòa nhà'
        verbose_name_plural = 'Danh sách Tòa nhà'

class Apartment(BaseModel):
    # 1. Các lựa chọn (Choices) chuẩn hóa dữ liệu
    STATUS_CHOICES = (
        ('VACANT', 'Đang mở bán/Trống'),
        ('OCCUPIED', 'Đã bàn giao/Đang ở'),
        ('BOOKED', 'Đã đặt cọc'),
        ('MAINTENANCE', 'Đang bảo trì'),
    )
    
    DIRECTION_CHOICES = (
        ('EAST', 'Đông'), ('WEST', 'Tây'), ('SOUTH', 'Nam'), ('NORTH', 'Bắc'),
        ('SE', 'Đông Nam'), ('SW', 'Tây Nam'), ('NE', 'Đông Bắc'), ('NW', 'Tây Bắc'),
    )

    ROOM_TYPE_CHOICES = (
        ('STUDIO', 'Studio'),
        ('1PN', '1 Phòng ngủ'),
        ('2PN', '2 Phòng ngủ'),
        ('3PN', '3 Phòng ngủ'),
        ('DUPLEX', 'Duplex'),
        ('PENTHOUSE', 'Penthouse'),
        ('SHOPHOUSE', 'Shophouse'),
    )
    
    FURNISHING_CHOICES = (
        ('RAW', 'Bàn giao thô'),
        ('BASIC', 'Nội thất cơ bản'),
        ('FULL', 'Full nội thất'),
    )

    # 2. Quan hệ & Vị trí
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='apartments', verbose_name="Tòa nhà")
    floor_number = models.IntegerField(verbose_name="Tầng số")
    unit_number = models.CharField(max_length=10, null=True, blank=True, verbose_name="Số căn (VD: 01)")
    apartment_code = models.CharField(max_length=50, unique=True, verbose_name="Mã căn hộ (Unique)")
    
    # 3. Thông tin Chủ sở hữu & Cư dân
    owner = models.ForeignKey(
        'residents.Resident', 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        related_name='owned_apartments',
        verbose_name="Chủ sở hữu hiện tại"
    )
    current_occupant_count = models.IntegerField(default=0, verbose_name="Số người đang ở")

    # 4. Thông tin Bán hàng & Kỹ thuật
    gross_area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Diện tích tim tường (m2)")
    net_area = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Diện tích thông thủy (m2)")
    
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, default='2PN', verbose_name="Loại phòng")
    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES, blank=True, verbose_name="Hướng ban công")
    
    price = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="Giá tham khảo (VNĐ)")
    
    # 5. Nội thất & Hình ảnh
    furnishing_type = models.CharField(max_length=20, choices=FURNISHING_CHOICES, default='BASIC', verbose_name="Tình trạng nội thất")
    furnishing_description = models.TextField(null=True, blank=True, verbose_name="Mô tả nội thất chi tiết")
    
    image = models.ImageField(upload_to='buildings/apartments/', null=True, blank=True, verbose_name="Hình ảnh đại diện")
    floor_plan_image = models.ImageField(upload_to='buildings/floor_plans/', null=True, blank=True, verbose_name="Sơ đồ mặt bằng căn")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='VACANT', verbose_name="Trạng thái")
    note = models.TextField(null=True, blank=True, verbose_name="Ghi chú BQL")

    bedrooms = models.IntegerField(default=1, verbose_name="Số PN")
    bathrooms = models.IntegerField(default=1, verbose_name="Số WC")
    area_m2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.apartment_code} ({self.building.name})"

    class Meta:
        db_table = 'apartments'
        ordering = ['building', 'floor_number', 'unit_number']
        verbose_name = 'Căn hộ'
        verbose_name_plural = 'Danh sách Căn hộ'