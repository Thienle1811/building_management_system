from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from .forms import StaffProfileForm, StaffCreationForm, ShiftConfigForm
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import StaffProfile, ShiftConfig

# Import các models cần thiết
from .models import StaffProfile, MaintenanceTask

@login_required
def roster_calendar_view(request):
    """Render giao diện xếp lịch trực"""
    return render(request, 'operation/roster.html')

@login_required
def performance_dashboard(request):
    """Báo cáo hiệu suất vận hành"""
    # 1. Thống kê tổng quan Task
    total_tasks = MaintenanceTask.objects.count()
    completed_tasks = MaintenanceTask.objects.filter(status='COMPLETED').count()
    pending_tasks = MaintenanceTask.objects.filter(status='PENDING').count()
    
    # 2. Thống kê theo Tổ (Dùng cho Biểu đồ tròn)
    # Đếm số task đã hoàn thành bởi từng tổ
    team_stats = MaintenanceTask.objects.filter(status='COMPLETED').values('staff__team').annotate(
        count=Count('id')
    ).order_by('staff__team')

    # Chuẩn bị dữ liệu cho Chart.js
    chart_labels = []
    chart_data = []
    for stat in team_stats:
        team_name = dict(StaffProfile.TEAM_CHOICES).get(stat['staff__team'], 'Chưa phân tổ')
        chart_labels.append(team_name)
        chart_data.append(stat['count'])

    # 3. Bảng xếp hạng Nhân viên & MTTR (Thời gian xử lý trung bình)
    # MTTR = Completed_At - Started_At
    staff_performance = StaffProfile.objects.annotate(
        total_assigned=Count('tasks'),
        completed_count=Count('tasks', filter=Q(tasks__status='COMPLETED')),
    ).filter(total_assigned__gt=0) # Chỉ lấy ai đã được giao việc

    # Tính MTTR thủ công (Do SQLite hạn chế tính toán thời gian phức tạp)
    performance_list = []
    for staff in staff_performance:
        tasks = staff.tasks.filter(status='COMPLETED', started_at__isnull=False, completed_at__isnull=False)
        avg_time_minutes = 0
        if tasks.exists():
            total_duration = sum((t.completed_at - t.started_at).total_seconds() for t in tasks)
            avg_time_minutes = (total_duration / tasks.count()) / 60 # Đổi ra phút
        
        performance_list.append({
            'full_name': staff.user.get_full_name() or staff.user.username,
            'team': staff.get_team_display(),
            'total': staff.total_assigned,
            'completed': staff.completed_count,
            'mttr': round(avg_time_minutes, 1) # Làm tròn 1 số lẻ
        })

    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'performance_list': performance_list
    }
    return render(request, 'operation/report.html', context)

@login_required
def staff_list_view(request):
    """Danh sách nhân viên"""
    staffs = StaffProfile.objects.select_related('user').all().order_by('team', 'user__first_name')
    return render(request, 'operation/setup/staff_list.html', {'staffs': staffs})

@login_required
def staff_create_view(request):
    """Thêm nhân viên mới"""
    if request.method == 'POST':
        form = StaffCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Thêm nhân viên thành công!")
            return redirect('operation:staff_list')
    else:
        form = StaffCreationForm()
    return render(request, 'operation/setup/staff_form.html', {'form': form, 'title': 'Thêm Nhân viên'})

@login_required
def staff_update_view(request, pk):
    """Sửa thông tin nhân viên"""
    staff = get_object_or_404(StaffProfile, pk=pk)
    if request.method == 'POST':
        form = StaffProfileForm(request.POST, request.FILES, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(request, "Cập nhật hồ sơ thành công!")
            return redirect('operation:staff_list')
    else:
        form = StaffProfileForm(instance=staff)
    return render(request, 'operation/setup/staff_form.html', {'form': form, 'title': 'Sửa Nhân viên'})

@login_required
def staff_delete_view(request, pk):
    """Xóa nhân viên (Xóa cả User)"""
    staff = get_object_or_404(StaffProfile, pk=pk)
    if request.method == 'POST':
        user = staff.user
        staff.delete()
        user.delete() # Xóa luôn tài khoản đăng nhập
        messages.success(request, "Đã xóa nhân viên.")
        return redirect('operation:staff_list')
    return render(request, 'operation/setup/staff_confirm_delete.html', {'staff': staff})

# --- CẤU HÌNH CA TRỰC ---
@login_required
def shift_list_view(request):
    """Danh sách Ca trực (Và sửa trực tiếp nếu muốn)"""
    shifts = ShiftConfig.objects.all().order_by('start_time')
    return render(request, 'operation/setup/shift_list.html', {'shifts': shifts})

@login_required
def shift_update_view(request, pk):
    """Sửa Ca trực"""
    shift = get_object_or_404(ShiftConfig, pk=pk)
    if request.method == 'POST':
        form = ShiftConfigForm(request.POST, instance=shift)
        if form.is_valid():
            form.save()
            messages.success(request, "Cập nhật ca trực thành công!")
            return redirect('operation:shift_list')
    else:
        form = ShiftConfigForm(instance=shift)
    return render(request, 'operation/setup/shift_form.html', {'form': form})