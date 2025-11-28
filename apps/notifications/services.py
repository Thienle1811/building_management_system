import logging
from django.utils import timezone
from datetime import timedelta
from .models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)

# Cấu hình khung giờ yên lặng (Có thể đưa vào settings sau này)
QUIET_HOUR_START = 23 # 23:00
QUIET_HOUR_END = 6    # 06:00 sáng hôm sau

class NotificationService:
    @staticmethod
    def send_feedback_notification(feedback, old_status, new_status):
        """
        Xử lý logic gửi thông báo khi trạng thái Feedback thay đổi.
        """
        # 1. Xác định nội dung (Template)
        title = ""
        body = ""
        
        if new_status == 'PROCESSING':
            title = "Phản hồi đang được xử lý"
            body = f"Phản hồi {feedback.code} của căn hộ {feedback.apartment.apartment_code} đang được Ban Quản Lý xử lý."
        elif new_status == 'DONE':
            title = "Phản hồi đã hoàn thành"
            body = f"Phản hồi {feedback.code} của căn hộ {feedback.apartment.apartment_code} đã được xử lý xong. Vui lòng kiểm tra kết quả."
        elif new_status == 'CANCELLED':
            title = "Phản hồi bị hủy"
            body = f"Phản hồi {feedback.code} đã bị hủy. Vui lòng liên hệ BQL để biết thêm chi tiết."
        else:
            return # Các trạng thái khác không cần báo

        # 2. Tìm người nhận (User tương ứng với Resident)
        # Giả định username của User là số điện thoại resident
        try:
            recipient = User.objects.get(username=feedback.resident.phone_number)
        except User.DoesNotExist:
            logger.warning(f"Không tìm thấy User cho Resident {feedback.resident.phone_number} để gửi Noti.")
            return

        # 3. Kiểm tra khung giờ yên lặng
        now = timezone.localtime(timezone.now())
        current_hour = now.hour
        
        scheduled_time = now # Mặc định gửi ngay
        
        # Nếu đang trong giờ yên lặng (23h -> 6h sáng)
        if current_hour >= QUIET_HOUR_START or current_hour < QUIET_HOUR_END:
            # Tính thời gian 6:30 sáng hôm sau (hoặc hôm nay nếu đang là sáng sớm)
            if current_hour >= QUIET_HOUR_START:
                target_date = now.date() + timedelta(days=1)
            else:
                target_date = now.date()
            
            # Set lịch là 06:30 sáng
            scheduled_time = now.replace(
                year=target_date.year, month=target_date.month, day=target_date.day,
                hour=6, minute=30, second=0, microsecond=0
            )
            logger.info(f"Noti rơi vào giờ yên lặng ({current_hour}h). Đã hoãn đến {scheduled_time}")

        # 4. Tạo bản ghi Notification
        notification = Notification.objects.create(
            recipient=recipient,
            title=title,
            body=body,
            notification_type='FEEDBACK_UPDATE',
            reference_id=str(feedback.id),
            scheduled_at=scheduled_time,
            is_sent=(scheduled_time == now) # Nếu gửi ngay thì đánh dấu sent luôn (giả lập)
        )
        
        # 5. Giả lập gửi Push (Integration với Firebase sẽ làm ở đây)
        if notification.is_sent:
            logger.info(f"🚀 [MOCK PUSH] Gửi ngay tới {recipient.username}: {title}")
            # send_fcm_message(recipient.fcm_token, title, body)...
        else:
            logger.info(f"zzz [QUEUED] Đã xếp hàng thông báo ID {notification.id}")