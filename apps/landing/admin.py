from django.contrib import admin
from .models import LandingConfig, HeroSlide, Benefit, FAQ

class HeroSlideInline(admin.StackedInline):
    model = HeroSlide
    extra = 1

class BenefitInline(admin.TabularInline):
    model = Benefit
    extra = 1

class FAQInline(admin.StackedInline):
    model = FAQ
    extra = 1

@admin.register(LandingConfig)
class LandingConfigAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'hotline', 'is_active', 'updated_at')
    inlines = [HeroSlideInline, BenefitInline, FAQInline]
    
    def has_add_permission(self, request):
        # Chỉ cho phép tạo tối đa 1 cấu hình active
        if self.model.objects.filter(is_active=True).exists():
            return False
        return True