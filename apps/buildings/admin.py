import logging
from django.contrib import admin
from django.contrib import messages
from .models import Building, Apartment

# Tạo logger để ghi nhật ký
logger = logging.getLogger(__name__)

class ApartmentInline(admin.TabularInline):
    """Cho phép thêm nhanh căn hộ ngay trong màn hình sửa Tòa nhà"""
    model = Apartment
    extra = 0
    fields = ('apartment_code', 'floor_number', 'room_type', 'net_area', 'status')
    show_change_link = True
    can_delete = False

@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'total_floors', 'units_per_floor_default', 'total_units_display', 'created_at')
    search_fields = ('name', 'code', 'address')
    inlines = [ApartmentInline]
    actions = ['generate_apartments_action']

    def total_units_display(self, obj):
        return obj.apartments.count()
    total_units_display.short_description = "Số căn hiện có"

    @admin.action(description="Khởi tạo tự động danh sách căn hộ (Skeleton)")
    def generate_apartments_action(self, request, queryset):
        total_created = 0
        for building in queryset:
            count = building.generate_apartments()
            total_created += count
            
            # --- LOGGING (MỚI) ---
            if count > 0:
                logger.info(f"PMS-03: User {request.user} đã sinh tự động {count} căn hộ cho tòa {building.name} ({building.code})")
            else:
                logger.warning(f"PMS-03: User {request.user} chạy sinh tự động cho tòa {building.name} nhưng không có căn nào được tạo.")
            # ---------------------
        
        self.message_user(request, f"Đã sinh tự động {total_created} căn hộ cho các tòa được chọn.", messages.SUCCESS)

@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
    list_display = ('apartment_code', 'building', 'floor_number', 'room_type', 'net_area', 'direction', 'owner', 'status')
    list_filter = ('building', 'status', 'room_type', 'direction', 'furnishing_type')
    search_fields = ('apartment_code', 'owner__full_name', 'owner__phone_number')
    
    fieldsets = (
        ('Vị trí & Mã', {
            'fields': ('building', 'floor_number', 'unit_number', 'apartment_code')
        }),
        ('Thông tin Bán hàng', {
            'fields': ('room_type', 'price', 'net_area', 'gross_area', 'direction')
        }),
        ('Trạng thái & Sở hữu', {
            'fields': ('status', 'owner', 'current_occupant_count')
        }),
        ('Nội thất & Hình ảnh', {
            'fields': ('furnishing_type', 'furnishing_description', 'image', 'floor_plan_image')
        }),
        ('Khác', {
            'fields': ('note',)
        }),
    )