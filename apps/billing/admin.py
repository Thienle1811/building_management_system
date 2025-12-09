from django.contrib import admin
from django.contrib import messages
from django.utils import timezone
from .models import ServiceConfig, PriceTier, VehicleType, InternetPackage, MeterReading, Invoice, InvoiceItem
from .services import BillingService

class PriceTierInline(admin.TabularInline):
    model = PriceTier
    extra = 1
    fields = ('tier_level', 'min_value', 'max_value', 'price')
    ordering = ('tier_level',)

@admin.register(ServiceConfig)
class ServiceConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_type', 'calculation_method', 'is_active')
    list_filter = ('service_type',)
    inlines = [PriceTierInline]

@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'monthly_price')

@admin.register(InternetPackage)
class InternetPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_active')

@admin.action(description='Tạo danh sách ghi số cho tháng hiện tại')
def generate_current_month_readings(modeladmin, request, queryset):
    now = timezone.now()
    count = BillingService.create_monthly_meter_readings(now.month, now.year)
    messages.success(request, f"Đã khởi tạo {count} bản ghi chỉ số cho tháng {now.month}/{now.year}.")

@admin.register(MeterReading)
class MeterReadingAdmin(admin.ModelAdmin):
    list_display = ('apartment', 'service_type', 'record_month', 'old_index', 'new_index', 'status')
    list_filter = ('record_month', 'service_type', 'status')
    actions = [generate_current_month_readings]

# --- ACTION TÍNH TIỀN (PHASE 3) ---
@admin.action(description='Tính tiền & Tạo hóa đơn (Bỏ qua căn chưa chốt số)')
def generate_current_month_invoices(modeladmin, request, queryset):
    now = timezone.now()
    # Logic Phase 3: Skip & Report
    count, skipped = BillingService.generate_monthly_invoices(now.month, now.year)
    
    msg = f"Đã lập thành công {count} hóa đơn cho tháng {now.month}/{now.year}."
    if skipped:
        skipped_str = ", ".join(skipped[:10]) 
        if len(skipped) > 10: skipped_str += "..."
        msg += f" [CẢNH BÁO] Đã BỎ QUA {len(skipped)} căn chưa có chỉ số: {skipped_str}."
        messages.warning(request, msg)
    else:
        messages.success(request, msg)

# --- ACTION XÁC NHẬN THANH TOÁN (PHASE 4 - MỚI) ---
@admin.action(description='Xác nhận ĐÃ THANH TOÁN')
def confirm_invoice_payment(modeladmin, request, queryset):
    # Chỉ xác nhận những đơn chưa thanh toán
    updated = queryset.exclude(status='PAID').update(
        status='PAID',
        payment_date=timezone.now()
    )
    messages.success(request, f"Đã xác nhận thanh toán thành công cho {updated} hóa đơn.")

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    readonly_fields = ('title', 'amount', 'description')
    can_delete = False

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    # Thêm cột has_proof vào danh sách hiển thị
    list_display = ('code', 'apartment', 'total_amount', 'status', 'month', 'year', 'has_proof')
    list_filter = ('status', 'month', 'year', 'apartment__building')
    search_fields = ('code', 'apartment__apartment_code')
    inlines = [InvoiceItemInline]
    
    # Đăng ký 2 actions quan trọng
    actions = [generate_current_month_invoices, confirm_invoice_payment]

    # Hàm hiển thị icon kiểm tra ảnh
    def has_proof(self, obj):
        return bool(obj.payment_proof)
    has_proof.boolean = True
    has_proof.short_description = "Có UNC?"