import logging
import requests
import json
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from .models import Notification, NotificationDevice

User = get_user_model()
logger = logging.getLogger(__name__)

# Cấu hình khung giờ yên lặng
QUIET_HOUR_START = 23
QUIET_HOUR_END = 6

class NotificationService:
    @staticmethod
    def send_push_to_user(user, title, body, data=None):
        # ... (Phần 1, 2, 3 giữ nguyên như cũ) ...
        # ...
        # 3. Tạo payload tin nhắn
        messages = []
        for token in push_tokens:
            messages.append({
                "to": token,
                "sound": "default",
                "title": title,
                "body": body,
                "data": data or {},
                "priority": "high",
                "channelId": "default",
            })

        # 4. Thực hiện gửi Request (SỬA ĐOẠN NÀY)
        try:
            response = requests.post(url, headers=headers, data=json.dumps(messages))
            
            # --- ĐOẠN CODE DEBUG QUAN TRỌNG ---
            response_data = response.json()
            
            if response.status_code == 200:
                # Kiểm tra từng vé gửi (Ticket) xem có lỗi không
                data_list = response_data.get('data', [])
                
                # In toàn bộ phản hồi ra để xem lỗi là gì
                print("🔍 [DEBUG EXPO RESPONSE]:", json.dumps(response_data, indent=2))
                
                for i, ticket in enumerate(data_list):
                    if ticket.get('status') == 'error':
                        error_msg = ticket.get('message')
                        error_details = ticket.get('details', {})
                        print(f"❌ [PUSH FAIL] Thiết bị {push_tokens[i]} bị lỗi: {error_msg} - {error_details}")
                    else:
                        print(f"✅ [PUSH SUCCESS] Đã gửi thành công tới: {push_tokens[i]}")
            else:
                print(f"❌ [PUSH ERROR] Lỗi Server Expo: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ [PUSH EXCEPTION] Lỗi kết nối: {str(e)}")

    @staticmethod
    def send_feedback_notification(feedback, old_status, new_status):
        """
        Xử lý logic nghiệp vụ phản hồi & Kiểm tra giờ yên lặng
        """
        # 1. Xác định nội dung
        title = ""
        body = ""
        
        if new_status == 'PROCESSING':
            title = "Phản hồi đang được xử lý"
            body = f"Yêu cầu '{feedback.title}' đang được Ban Quản Lý tiếp nhận và xử lý."
        elif new_status == 'DONE':
            title = "Phản hồi hoàn tất"
            body = f"Yêu cầu '{feedback.title}' của bạn đã được xử lý xong. Vui lòng kiểm tra."
        elif new_status == 'CANCELLED':
            title = "Phản hồi bị hủy"
            body = f"Yêu cầu '{feedback.title}' đã bị hủy. Vui lòng liên hệ BQL để biết thêm chi tiết."
        else:
            return

        # 2. Xác định người nhận
        recipient = None
        if hasattr(feedback.resident, 'user') and feedback.resident.user:
            recipient = feedback.resident.user
        else:
            try:
                recipient = User.objects.get(username=feedback.resident.phone_number)
            except User.DoesNotExist:
                print(f"⚠️ [LOGIC] Không tìm thấy tài khoản User cho cư dân SĐT: {feedback.resident.phone_number}")
                return

        # 3. Kiểm tra giờ yên lặng
        now = timezone.localtime(timezone.now())
        current_hour = now.hour
        
        # Lưu thông báo vào DB
        Notification.objects.create(
            recipient=recipient,
            title=title,
            body=body,
            notification_type='FEEDBACK_UPDATE',
            reference_id=str(feedback.id),
            is_read=False
        )

        if current_hour >= QUIET_HOUR_START or current_hour < QUIET_HOUR_END:
            print(f"zzz [SILENT] Đang là giờ yên lặng ({current_hour}h). Chỉ lưu DB, không gửi Push.")
            return

        # 4. Gửi Push Notification
        NotificationService.send_push_to_user(
            user=recipient, 
            title=title, 
            body=body, 
            data={'feedbackId': feedback.id, 'type': 'FEEDBACK_UPDATE'}
        )