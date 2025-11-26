from django.contrib import admin
from .models import LandingConfig, HeroSlide, Benefit, FAQ, ProcessStep, CustomerLead, NewsItem

# 1. Cấu hình chung cho các trường hệ thống
system_readonly_fields = ('created_at', 'updated_at', 'deleted_at')

class HeroSlideInline(admin.StackedInline):
    model = HeroSlide
    extra = 1
    readonly_fields = system_readonly_fields

class BenefitInline(admin.TabularInline):
    model = Benefit
    extra = 1
    readonly_fields = system_readonly_fields

class FAQInline(admin.StackedInline):
    model = FAQ
    extra = 1
    readonly_fields = system_readonly_fields

class ProcessStepInline(admin.TabularInline): 
    model = ProcessStep
    extra = 1
    readonly_fields = system_readonly_fields

@admin.register(LandingConfig)
class LandingConfigAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'hotline', 'is_active', 'updated_at', 'is_deleted')
    inlines = [HeroSlideInline, BenefitInline, ProcessStepInline, FAQInline]
    readonly_fields = system_readonly_fields
    
    def has_add_permission(self, request):
        if self.model.objects.filter(is_active=True).exists():
            return False
        return True

    def get_queryset(self, request):
        return self.model.all_objects.all()

    def is_deleted(self, obj):
        return obj.deleted_at is not None
    is_deleted.boolean = True
    is_deleted.short_description = "Đã xóa?"

# Đăng ký CustomerLead (MỚI)
@admin.register(CustomerLead)
class CustomerLeadAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'demand', 'created_at', 'status')
    search_fields = ('full_name', 'phone', 'email')
    list_filter = ('created_at', 'demand', 'status')
    readonly_fields = system_readonly_fields

# Đăng ký NewsItem (MỚI)
@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'created_at')
    readonly_fields = system_readonly_fields