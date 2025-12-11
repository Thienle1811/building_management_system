from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from datetime import date

from .models import Invoice, MeterReading, PriceTier
from .services import BillingService
from .forms import InvoiceForm
from apps.buildings.models import Apartment

# Decorator kiểm tra Staff
def is_staff_check(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_staff_check)
def invoice_list(request):
    """Danh sách hóa đơn"""
    invoices = Invoice.objects.all().order_by('-year', '-month', 'apartment__apartment_code')
    
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
def invoice_create(request):
    """Tạo hóa đơn thủ công (Lẻ)"""
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save()
            messages.success(request, f"Đã tạo hóa đơn cho căn hộ {invoice.apartment.apartment_code}!")
            return redirect('billing:invoice_list')
    else:
        form = InvoiceForm()
    return render(request, 'billing/invoice_form.html', {'form': form, 'title': 'Tạo Hóa đơn mới'})

@login_required
@user_passes_test(is_staff_check)
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'billing/invoice_detail.html', {'invoice': invoice})

@login_required
@user_passes_test(is_staff_check)
def invoice_confirm_payment(request, pk):
    if request.method == 'POST':
        confirmed = BillingService.confirm_payment_by_id(pk)
        if confirmed:
            messages.success(request, f"Đã xác nhận thanh toán thành công cho hóa đơn #{pk}.")
        else:
            messages.error(request, f"Không tìm thấy hóa đơn #{pk} hoặc đã thanh toán.")
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
                            MeterReading.objects.update_or_create(
                                apartment_id=apartment_id,
                                service_type=service_type,
                                record_year=year,
                                record_month=month,
                                defaults={'new_index': float(value), 'status': 'RECORDED'}
                            )
                            count += 1
            messages.success(request, f"Đã lưu thành công {count} chỉ số tháng {month}/{year}!")
        except Exception as e:
            messages.error(request, f"Lỗi khi lưu: {str(e)}")
        
        base_url = reverse('billing:meter_reading')
        return redirect(f'{base_url}?month={selected_month}')

    apartments = Apartment.objects.all().order_by('floor_number', 'unit_number')
    readings = MeterReading.objects.filter(record_year=year, record_month=month)
    
    data_map = {}
    for r in readings:
        if r.apartment_id not in data_map: data_map[r.apartment_id] = {}
        data_map[r.apartment_id][r.service_type] = r.new_index 

    context = {
        'apartments': apartments,
        'data_map': data_map,
        'selected_month': selected_month,
        'today_month': today.strftime('%Y-%m')
    }
    return render(request, 'billing/meter_reading.html', context)

@login_required
@user_passes_test(is_staff_check)
def generate_invoices_view(request):
    """Action: Chốt sổ & Tạo hóa đơn hàng loạt"""
    if request.method == 'POST':
        selected_month = request.POST.get('month') # Format YYYY-MM
        if not selected_month:
            messages.error(request, "Vui lòng chọn tháng.")
            return redirect('billing:meter_reading')

        try:
            year, month = map(int, selected_month.split('-'))
            
            # --- ĐÃ SỬA: Gọi đúng tên hàm trong services.py ---
            count, skipped = BillingService.generate_monthly_invoices(month, year)
            
            if count > 0:
                messages.success(request, f"Đã tạo thành công {count} hóa đơn tổng hợp (Điện/Nước/Xe/QL).")
            
            if skipped:
                # skipped là danh sách các mã căn hộ bị bỏ qua
                messages.warning(request, f"Bỏ qua {len(skipped)} căn hộ do chưa chốt chỉ số điện nước: {', '.join(skipped[:5])}...")
            
            if count == 0 and not skipped:
                messages.info(request, "Không có hóa đơn nào mới được tạo (có thể đã tạo hết rồi).")
                
        except Exception as e:
            messages.error(request, f"Lỗi hệ thống: {str(e)}")
            
        base_url = reverse('billing:meter_reading')
        return redirect(f'{base_url}?month={selected_month}')
    
    return redirect('billing:meter_reading')

@login_required
def price_config_view(request):
    """Cấu hình đơn giá"""
    if request.method == 'POST':
        try:
            count = 0
            for key, value in request.POST.items():
                if key.startswith('price_'):
                    parts = key.split('_')
                    if len(parts) == 2:
                        _, tier_id = parts
                        if value.strip():
                            PriceTier.objects.filter(id=tier_id).update(price=float(value))
                            count += 1
            messages.success(request, "Đã cập nhật đơn giá!")
        except Exception as e:
            messages.error(request, f"Lỗi: {str(e)}")
        return redirect('billing:price_config')

    # Fix lỗi query nếu model ServiceConfig thay đổi
    # Logic hiển thị đơn giá (tạm thời để trống hoặc giữ nguyên logic cũ của bạn)
    return render(request, 'billing/price_config.html')