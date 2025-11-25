from django.contrib import admin
from .models import Building, Apartment

class BaseAdmin(admin.ModelAdmin):
    """Admin cơ sở: Hiển thị cả file đã xóa & chặn sửa ngày xóa"""
    readonly_fields = ('deleted_at', 'created_at', 'updated_at')

    def get_queryset(self, request):
        # Sử dụng manager 'all_objects' để lấy TẤT CẢ (kể cả đã xóa)
        return self.model.all_objects.get_queryset()

@admin.register(Building)
class BuildingAdmin(BaseAdmin): # Kế thừa từ BaseAdmin
    list_display = ('name', 'address', 'total_floors', 'is_deleted')
    
    # Hiển thị cột trạng thái xóa cho dễ nhìn
    def is_deleted(self, obj):
        return obj.deleted_at is not None
    is_deleted.boolean = True
    is_deleted.short_description = "Đã xóa?"

@admin.register(Apartment)
class ApartmentAdmin(BaseAdmin): # Kế thừa từ BaseAdmin
    list_display = ('apartment_code', 'building', 'floor_number', 'status', 'is_deleted')
    list_filter = ('building', 'status')
    search_fields = ('apartment_code',)

    def is_deleted(self, obj):
        return obj.deleted_at is not None
    is_deleted.boolean = True
    is_deleted.short_description = "Đã xóa?"