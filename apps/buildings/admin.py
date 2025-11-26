from django.contrib import admin
from .models import Building, Apartment

class BaseAdmin(admin.ModelAdmin):
    """Admin cơ sở: Hiển thị cả file đã xóa & chặn sửa ngày xóa"""
    
    # --- KHẮC PHỤC: Bỏ 'deleted_at' khỏi readonly_fields ---
    readonly_fields = ('created_at', 'updated_at')
    
    # --- KHẮC PHỤC: Thêm exclude để ẩn hoàn toàn khỏi form ---
    exclude = ('deleted_at',)

    def get_queryset(self, request):
        # Sử dụng manager 'all_objects' để lấy TẤT CẢ (kể cả đã xóa)
        return self.model.all_objects.get_queryset()

# Inline để thêm nhanh căn hộ khi đang sửa Tòa nhà (Giữ lại logic cũ)
class ApartmentInline(admin.TabularInline):
    model = Apartment
    extra = 1
    exclude = ('deleted_at',) # Ẩn luôn trong bảng con

@admin.register(Building)
class BuildingAdmin(BaseAdmin): # Kế thừa từ BaseAdmin đã sửa
    list_display = ('name', 'address', 'total_floors', 'is_deleted')
    search_fields = ('name', 'address')
    inlines = [ApartmentInline]
    
    def is_deleted(self, obj):
        return obj.deleted_at is not None
    is_deleted.boolean = True
    is_deleted.short_description = "Đã xóa?"

@admin.register(Apartment)
class ApartmentAdmin(BaseAdmin): # Kế thừa từ BaseAdmin đã sửa
    # Hiển thị đầy đủ thông tin (bao gồm các trường Catalog nếu đã thêm)
    list_display = ('apartment_code', 'building', 'floor_number', 'area_m2', 'status', 'is_deleted')
    list_filter = ('building', 'status')
    search_fields = ('apartment_code', 'building__name')
    
    # Nếu bạn đã thêm trường 'price' và 'bedrooms' ở bước trước, hãy bỏ comment dòng dưới:
    # list_editable = ('status', 'price') 

    def is_deleted(self, obj):
        return obj.deleted_at is not None
    is_deleted.boolean = True
    is_deleted.short_description = "Đã xóa?"