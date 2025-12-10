from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.contrib import messages
from .models import Invoice, InvoiceItem
from .services import BillingService
from django.utils import timezone

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