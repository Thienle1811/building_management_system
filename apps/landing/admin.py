from django.contrib import admin
from .models import LandingConfig, HeroSlide, Benefit, FAQ, ProcessStep, CustomerLead, NewsItem

# 1. Định nghĩa các trường hệ thống sẽ hiển thị (Tuyệt đối KHÔNG có deleted_at)
system_readonly_fields = ('created_at', 'updated_at')

class HeroSlideInline(admin.StackedInline):
    model = HeroSlide
    extra = 1
    # Ẩn deleted_at bằng cách chỉ hiện các trường cần thiết hoặc dùng exclude
    exclude = ('deleted_at',)
    readonly_fields = system_readonly_fields

class BenefitInline(admin.TabularInline):
    model = Benefit
    extra = 1
    exclude = ('deleted_at',)
    readonly_fields = system_readonly_fields

class FAQInline(admin.StackedInline):
    model = FAQ
    extra = 1
    exclude = ('deleted_at',)
    readonly_fields = system_readonly_fields

class ProcessStepInline(admin.TabularInline): 
    model = ProcessStep
    extra = 1
    exclude = ('deleted_at',)
    readonly_fields = system_readonly_fields

@admin.register(LandingConfig)
class LandingConfigAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'hotline', 'is_active', 'updated_at')
    
    inlines = [HeroSlideInline, BenefitInline, ProcessStepInline, FAQInline]
    
    # Sử dụng exclude để loại bỏ deleted_at khỏi form chính
    exclude = ('deleted_at',)
    readonly_fields = system_readonly_fields
    
    def has_add_permission(self, request):
        if self.model.objects.filter(is_active=True).exists():
            return False
        return True

    def get_queryset(self, request):
        return self.model.all_objects.all()

@admin.register(CustomerLead)
class CustomerLeadAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'demand', 'created_at', 'status')
    search_fields = ('full_name', 'phone', 'email')
    list_filter = ('created_at', 'demand', 'status')
    
    # --- KHẮC PHỤC TRIỆT ĐỂ: Chỉ định rõ các trường được hiện ---
    fields = ('full_name', 'phone', 'email', 'demand', 'note', 'status', 'created_at', 'updated_at')
    
    # Chỉ các trường trong danh sách này mới được hiện dạng Read-only
    readonly_fields = system_readonly_fields

@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'created_at')
    
    # --- KHẮC PHỤC TRIỆT ĐỂ ---
    fields = ('title', 'image', 'link', 'date', 'created_at', 'updated_at')
    
    readonly_fields = system_readonly_fields