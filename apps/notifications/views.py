import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import Notification
from .forms import SystemNotificationForm # Import Form mới
from apps.residents.models import Resident

User = get_user_model()
logger = logging.getLogger(__name__)

@login_required
def notification_list(request):
    """Danh sách thông báo của người dùng hiện tại"""
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    context = {
        'notifications': notifications,
        'title': 'Thông báo hệ thống'
    }
    return render(request, 'notifications/notification_list.html', context)

@login_required
def notification_create(request):
    """BQL tạo thông báo mới gửi cho cư dân"""
    # Kiểm tra quyền (chỉ Admin/Staff mới được gửi)
    if not request.user.is_staff:
        messages.error(request, "Bạn không có quyền gửi thông báo hệ thống.")
        return redirect('notification_list')

    if request.method == 'POST':
        form = SystemNotificationForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            body = form.cleaned_data['body']
            target = form.cleaned_data['target_group']
            
            recipients = []
            
            # 1. Lọc danh sách người nhận
            if target == 'ALL':
                # Lấy tất cả User có liên kết với Resident
                # (Logic: username trùng với số điện thoại của resident)
                resident_phones = Resident.objects.values_list('phone_number', flat=True)
                recipients = User.objects.filter(username__in=resident_phones)
                
            elif target == 'OWNERS':
                owner_phones = Resident.objects.filter(relationship_type='OWNER').values_list('phone_number', flat=True)
                recipients = User.objects.filter(username__in=owner_phones)

            # 2. Tạo thông báo hàng loạt (Bulk Create)
            if recipients:
                notification_list = []
                for user in recipients:
                    notification_list.append(Notification(
                        recipient=user,
                        title=title,
                        body=body,
                        notification_type='SYSTEM',
                        is_sent=True, # Giả định gửi luôn (hoặc dùng service check giờ yên lặng)
                        # scheduled_at=... (Nếu muốn hẹn giờ)
                    ))
                
                with transaction.atomic():
                    Notification.objects.bulk_create(notification_list)
                
                # TODO: Tại đây gọi Firebase/Expo Service để bắn Push Notification thật
                # send_mass_push_notification(recipients, title, body)
                
                msg = f"Đã gửi thông báo thành công tới {len(notification_list)} cư dân."
                logger.info(f"User {request.user} sent system notification: '{title}' to {len(notification_list)} users.")
                messages.success(request, msg)
                return redirect('notification_list')
            else:
                messages.warning(request, "Không tìm thấy người nhận phù hợp.")
    else:
        form = SystemNotificationForm()

    return render(request, 'notifications/notification_form.html', {
        'form': form,
        'title': 'Tạo Thông báo Mới'
    })

@login_required
def mark_all_read(request):
    """Đánh dấu tất cả là đã đọc"""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    messages.success(request, "Đã đánh dấu tất cả là đã đọc.")
    return redirect('notification_list')