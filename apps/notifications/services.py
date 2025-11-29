import logging
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from exponent_server_sdk import (
    PushClient,
    PushMessage,
    PushServerError,
    DeviceNotRegisteredError
)
from .models import Notification, NotificationDevice

User = get_user_model()
logger = logging.getLogger(__name__)

# Cấu hình khung giờ yên lặng
QUIET_HOUR_START = 23
QUIET_HOUR_END = 6

class NotificationService:
    @staticmethod
    def send_push_to_user(user, title, body, data=None):
        """Hàm gửi Push thật sự qua Expo"""
        # 1. Lấy tất cả token của user này
        devices = NotificationDevice.objects.filter(user=user)
        if not devices.exists():
            logger.info(f"User {user.username} không có thiết bị nào đăng ký Push.")
            return

        # 2. Chuẩn bị tin nhắn
        messages = []
        for device in devices:
            try:
                messages.append(
                    PushMessage(
                        to=device.expo_push_token,
                        title=title,
                        body=body,
                        data=data,
                        sound='default', # Âm thanh mặc định
                        badge=1
                    )
                )
            except Exception as e:
                logger.error(f"Lỗi tạo tin nhắn cho token {device.expo_push_token}: {e}")

        # 3. Gửi đi
        if messages:
            try:
                client = PushClient()
                responses = client.publish_multiple(messages)
                logger.info(f"🚀 Đã gửi {len(responses)} thông báo tới User {user.username}")
            except Exception as e:
                logger.error(f"Lỗi gửi Push Expo: {e}", exc_info=True)

    @staticmethod
    def send_feedback_notification(feedback, old_status, new_status):
        """Xử lý logic nghiệp vụ & Giờ yên lặng"""
        # 1. Xác định nội dung (Như cũ)
        title = ""
        body = ""
        
        if new_status == 'PROCESSING':
            title = "Phản hồi đang được xử lý"
            body = f"Yêu cầu '{feedback.title}' đang được BQL xử lý."
        elif new_status == 'DONE':
            title = "Phản hồi hoàn tất"
            body = f"Yêu cầu '{feedback.title}' đã được xử lý xong."
        elif new_status == 'CANCELLED':
            title = "Phản hồi bị hủy"
            body = f"Yêu cầu '{feedback.title}' đã bị hủy."
        else:
            return

        recipient = feedback.resident.user_account # (Lưu ý: Cần chắc chắn Resident có link tới User)
        # Nếu logic cũ bạn dùng User.objects.get(username=phone) thì giữ nguyên:
        try:
            recipient = User.objects.get(username=feedback.resident.phone_number)
        except User.DoesNotExist:
            return

        # 2. Kiểm tra giờ yên lặng (Như cũ)
        now = timezone.localtime(timezone.now())
        current_hour = now.hour
        scheduled_time = now
        
        if current_hour >= QUIET_HOUR_START or current_hour < QUIET_HOUR_END:
            # Logic hẹn giờ (giữ nguyên như bài trước)
            if current_hour >= QUIET_HOUR_START:
                target_date = now.date() + timedelta(days=1)
            else:
                target_date = now.date()
            scheduled_time = now.replace(year=target_date.year, month=target_date.month, day=target_date.day, hour=6, minute=30)
            
            # Chỉ lưu DB, không gửi Push ngay
            Notification.objects.create(
                recipient=recipient, title=title, body=body,
                notification_type='FEEDBACK_UPDATE', reference_id=str(feedback.id),
                scheduled_at=scheduled_time, is_sent=False
            )
            logger.info(f"zzz Hoãn thông báo đến {scheduled_time}")
            return

        # 3. Gửi NGAY LẬP TỨC
        # Lưu DB
        Notification.objects.create(
            recipient=recipient, title=title, body=body,
            notification_type='FEEDBACK_UPDATE', reference_id=str(feedback.id),
            scheduled_at=now, is_sent=True
        )
        
        # Gửi Push thật
        NotificationService.send_push_to_user(recipient, title, body, data={'feedbackId': feedback.id})