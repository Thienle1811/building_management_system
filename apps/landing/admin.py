from django.contrib import admin
from .models import LandingConfig, HeroSlide, Benefit, FAQ

# 1. Cấu hình chung cho các trường hệ thống
# Để ngăn người dùng sửa tay ngày xóa/ngày tạo
system_readonly_fields = ('created_at', 'updated_at', 'deleted_at')

class HeroSlideInline(admin.StackedInline):
    model = HeroSlide
    extra = 1
    readonly_fields = system_readonly_fields  # <--- Chặn sửa ngày xóa

class BenefitInline(admin.TabularInline):
    model = Benefit
    extra = 1
    readonly_fields = system_readonly_fields  # <--- Chặn sửa ngày xóa

class FAQInline(admin.StackedInline):
    model = FAQ
    extra = 1
    readonly_fields = system_readonly_fields  # <--- Chặn sửa ngày xóa

@admin.register(LandingConfig)
class LandingConfigAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'hotline', 'is_active', 'updated_at', 'is_deleted')
    inlines = [HeroSlideInline, BenefitInline, FAQInline]
    readonly_fields = system_readonly_fields  # <--- Chặn sửa ngày xóa ở bảng cha
    
    def has_add_permission(self, request):
        # Chỉ cho phép tạo tối đa 1 cấu hình active
        # Lưu ý: Sử dụng all_objects để check cả những bản ghi đã xóa mềm nếu cần
        if self.model.objects.filter(is_active=True).exists():
            return False
        return True

    def get_queryset(self, request):
        # Hiển thị cả bản ghi đã xóa mềm để Admin quản lý
        return self.model.all_objects.all()

    def is_deleted(self, obj):
        return obj.deleted_at is not None
    is_deleted.boolean = True
    is_deleted.short_description = "Đã xóa?"