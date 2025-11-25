from django.contrib import admin
from .models import Resident, Vehicle

class VehicleInline(admin.TabularInline):
    """Cho phép thêm xe ngay trong màn hình chi tiết cư dân"""
    model = Vehicle
    extra = 1

@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'identity_card', 'phone_number', 'current_apartment', 'relationship_type')
    list_filter = ('relationship_type', 'current_apartment__building')
    search_fields = ('full_name', 'identity_card', 'phone_number')
    inlines = [VehicleInline] # Nhúng bảng xe vào đây