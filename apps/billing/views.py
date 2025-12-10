from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.contrib import messages
from .models import Invoice, InvoiceItem, MeterReading, PriceTier
from .services import BillingService
from django.utils import timezone
from datetime import date
from apps.buildings.models import Apartment

# Decorator kiểm tra người dùng phải là Staff (BQL)
def is_staff_check(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_staff_check)
def invoice_list(request):
    """Hiển thị danh sách hóa đơn cho BQL"""
    invoices = Invoice.objects.all().order_by('-year', '-month', 'apartment__apartment_code')
    
    # Lọc theo trạng thái và tháng/năm (Filter logic đơn giản)
    status_filter = request.GET.get('status')
    month_filter = request.GET.get('month')
    year_filter = request.GET.get('year')

    if status_filter:
        invoices = invoices.filter(status=status_filter)
    if month_filter and month_filter.isdigit():
        invoices = invoices.filter(month=month_filter)
    if year_filter and year_filter.isdigit():
        invoices = invoices.filter(year=year_filter)
        
    context = {
        'invoices': invoices,
        'current_month': timezone.now().month,
        'current_year': timezone.now().year,
        'status_choices': Invoice.STATUS_CHOICES,
        'active_status': status_filter
    }
    return render(request, 'billing/invoice_list.html', context)

@login_required
@user_passes_test(is_staff_check)
def invoice_detail(request, pk):
    """Hiển thị chi tiết hóa đơn (bao gồm ảnh chuyển khoản)"""
    invoice = get_object_or_404(Invoice, pk=pk)
    context = {
        'invoice': invoice,
    }
    return render(request, 'billing/invoice_detail.html', context)

@login_required
@user_passes_test(is_staff_check)
def invoice_confirm_payment(request, pk):
    """Xử lý POST request khi BQL bấm nút xác nhận thanh toán"""
    if request.method == 'POST':
        confirmed = BillingService.confirm_payment_by_id(pk)
        if confirmed:
            messages.success(request, f"Đã xác nhận thanh toán thành công cho hóa đơn #{pk}.")
        else:
            messages.error(request, f"Không tìm thấy hóa đơn #{pk} hoặc hóa đơn đã được thanh toán rồi.")
    
    # Chuyển hướng về trang chi tiết hóa đơn
    return redirect('billing:invoice_detail', pk=pk)
@login_required
def meter_reading_view(request):
    """Giao diện Ghi chỉ số Điện/Nước"""
    today = date.today()
    selected_month = request.GET.get('month', today.strftime('%Y-%m'))
    try:
        year, month = map(int, selected_month.split('-'))
    except ValueError:
        year, month = today.year, today.month

    if request.method == 'POST':
        try:
            count = 0
            for key, value in request.POST.items():
                if key.startswith('reading_'):
                    parts = key.split('_')
                    if len(parts) == 3:
                        _, apartment_id, service_type = parts
                        if value.strip(): 
                            # --- SỬA LỖI 1: Dùng đúng tên trường record_year, record_month, new_index ---
                            MeterReading.objects.update_or_create(
                                apartment_id=apartment_id,
                                service_type=service_type,
                                record_year=year,    # Sửa từ date__year
                                record_month=month,  # Sửa từ date__month
                                defaults={
                                    'new_index': float(value), # Sửa từ reading_value
                                    # Bỏ dòng 'date': ... vì model không có trường date
                                }
                            )
                            count += 1
            messages.success(request, f"Đã lưu thành công {count} chỉ số tháng {month}/{year}!")
        except Exception as e:
            messages.error(request, f"Lỗi khi lưu: {str(e)}")
        return redirect(f'?month={selected_month}')

    # Lấy danh sách căn hộ (đã sửa floor_number, unit_number từ bước trước)
    apartments = Apartment.objects.all().order_by('floor_number', 'unit_number')
    
    # --- SỬA LỖI 2: Filter đúng tên trường ---
    readings = MeterReading.objects.filter(record_year=year, record_month=month)
    
    data_map = {}
    for r in readings:
        if r.apartment_id not in data_map:
            data_map[r.apartment_id] = {}
        # --- SỬA LỖI 3: Lấy đúng trường new_index ---
        data_map[r.apartment_id][r.service_type] = r.new_index 

    context = {
        'apartments': apartments,
        'data_map': data_map,
        'selected_month': selected_month,
        'today_month': today.strftime('%Y-%m')
    }
    return render(request, 'billing/meter_reading.html', context)

@login_required
def price_config_view(request):
    """Giao diện Cấu hình Đơn giá"""
    if request.method == 'POST':
        try:
            count = 0
            for key, value in request.POST.items():
                if key.startswith('price_'):
                    # Key format: price_1 (1 là ID của PriceTier)
                    parts = key.split('_')
                    if len(parts) == 2:
                        _, tier_id = parts
                        if value.strip():
                            PriceTier.objects.filter(id=tier_id).update(price=float(value)) # Sửa unit_price thành price
                            count += 1
            messages.success(request, "Đã cập nhật đơn giá thành công!")
        except Exception as e:
            messages.error(request, f"Lỗi cập nhật: {str(e)}")
        return redirect('billing:price_config')

    # --- SỬA LỖI Ở ĐÂY ---
    # 1. Dùng config__service_type để lọc qua bảng cha
    # 2. Dùng config__is_active=True để chỉ lấy bảng giá đang áp dụng
    # 3. Sắp xếp theo min_value (thay vì min_usage)
    electricity_tiers = PriceTier.objects.filter(
        config__service_type='ELECTRICITY',
        config__is_active=True
    ).order_by('min_value')
    
    water_tiers = PriceTier.objects.filter(
        config__service_type='WATER',
        config__is_active=True
    ).order_by('min_value')
    
    return render(request, 'billing/price_config.html', {
        'electricity_tiers': electricity_tiers,
        'water_tiers': water_tiers
    })