from django.contrib import admin
from .models import Contract

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    # Các trường hiển thị trên danh sách
    list_display = ('code', 'apartment', 'resident', 'contract_type', 'status', 'start_date', 'end_date')
    
    # Bộ lọc bên phải
    list_filter = ('status', 'contract_type', 'start_date')
    
    # Thanh tìm kiếm (tìm theo Mã HĐ, Tên cư dân, Mã căn hộ)
    search_fields = ('code', 'resident__full_name', 'apartment__apartment_code')
    
    # Thanh điều hướng theo ngày tạo
    date_hierarchy = 'created_at'