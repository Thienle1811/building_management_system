from celery import shared_task
from django.utils import timezone
from .models import Notification
from .services import NotificationService

@shared_task
def send_push_notification_task(notification_id):
    """
    Task gửi thông báo ngay lập tức (Async).
    Sau này tích hợp Firebase/Expo sẽ viết code gọi API vào đây.
    """
    try:
        notification = Notification.objects.get(id=notification_id)
        
        # --- LOGIC GỬI PUSH (MOCKUP) ---
        # Hiện tại chưa có Firebase, ta chỉ in log ra màn hình Console của Worker
        print(f"========================================")
        print(f"🚀 [CELERY] Đang gửi thông báo: {notification.title}")
        print(f"📩 Nội dung: {notification.content}")
        print(f"👥 Gửi đến: {notification.recipients.count()} người")
        
        # Giả lập độ trễ mạng (nếu cần test async)
        # import time; time.sleep(5)
        
        print(f"✅ [CELERY] Gửi thành công!")
        print(f"========================================")
        
        # Cập nhật trạng thái đã gửi (nếu chưa)
        if not notification.is_sent:
            notification.is_sent = True
            notification.sent_at = timezone.now()
            notification.save()
            
    except Notification.DoesNotExist:
        print(f"❌ [CELERY] Không tìm thấy thông báo ID {notification_id}")

@shared_task
def send_scheduled_notifications():
    """
    Task chạy định kỳ (mỗi phút) để quét các tin hẹn giờ
    """
    now = timezone.now()
    
    # Tìm các tin: Chưa gửi VÀ Có hẹn giờ VÀ Giờ hẹn <= Hiện tại
    pending_notifications = Notification.objects.filter(
        is_sent=False,
        scheduled_at__lte=now
    )
    
    count = pending_notifications.count()
    if count > 0:
        print(f"⏰ [BEAT] Tìm thấy {count} thông báo đến giờ gửi.")
        for notification in pending_notifications:
            # Gửi tin & Đánh dấu đã gửi
            # Gọi lại task send_push bên trên để tái sử dụng logic
            send_push_notification_task.delay(notification.id)
            
            # Cập nhật tạm thời để tránh task sau quét lại trúng (dù task kia sẽ update sau)
            notification.is_sent = True 
            notification.sent_at = timezone.now()
            notification.save()