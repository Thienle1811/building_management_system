from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Notification, NotificationRecipient
from .forms import NotificationForm
from .services import NotificationService

@login_required
def notification_list(request):
    """Xem danh sách thông báo"""
    user = request.user
    
    if user.is_staff:
        # Admin thấy hết
        notifications = Notification.objects.all().order_by('-created_at')
    else:
        # Cư dân chỉ thấy tin của mình
        notifications = Notification.objects.filter(recipients__recipient=user).order_by('-created_at')

    return render(request, 'notifications/notification_list.html', {'notifications': notifications})

@login_required
def notification_create(request):
    """Tạo thông báo mới (Admin) - Có logic hẹn giờ"""
    if not request.user.is_staff:
        messages.error(request, "Bạn không có quyền thực hiện chức năng này.")
        return redirect('notification_list')

    if request.method == 'POST':
        form = NotificationForm(request.POST, request.FILES)
        if form.is_valid():
            notification = form.save(commit=False)
            
            # --- LOGIC HẸN GIỜ (PHASE 4) ---
            now = timezone.now()
            
            # Kiểm tra nếu có giờ hẹn VÀ giờ hẹn ở tương lai
            if notification.scheduled_at and notification.scheduled_at > now:
                notification.is_sent = False
                msg = f"Đã lên lịch gửi vào {notification.scheduled_at.strftime('%H:%M %d/%m/%Y')}."
            else:
                # Gửi ngay lập tức
                notification.is_sent = True
                notification.sent_at = now
                msg = "Đã gửi thông báo thành công."
            
            notification.save()
            
            # Tạo danh sách người nhận ngay lập tức (dù gửi ngay hay chờ)
            count = NotificationService.create_notification_recipients(notification)
            
            messages.success(request, f"{msg} (cho {count} cư dân).")
            return redirect('notification_list')
    else:
        form = NotificationForm()
    
    return render(request, 'notifications/notification_form.html', {'form': form})

@login_required
def notification_mark_read(request):
    """Đánh dấu TẤT CẢ là đã đọc cho user hiện tại"""
    updated_count = NotificationRecipient.objects.filter(
        recipient=request.user, 
        is_read=False
    ).update(is_read=True, read_at=timezone.now())
    
    if updated_count > 0:
        messages.success(request, f"Đã đánh dấu {updated_count} thông báo là đã đọc.")
    else:
        messages.info(request, "Không có thông báo nào mới.")
        
    return redirect('notification_list')