from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from apps.residents.models import Resident
from apps.buildings.models import Apartment
from .models import Notification, NotificationRecipient

User = get_user_model()

class NotificationService:
    """
    Service xử lý logic nghiệp vụ cho Thông báo
    """

    @staticmethod
    def create_notification_recipients(notification):
        """
        Hàm này được gọi ngay sau khi Notification được tạo.
        Nó sẽ quét Target Type để tìm users và tạo NotificationRecipient.
        """
        target_type = notification.target_type
        identifier = notification.target_identifier
        
        users = []

        # --- LOGIC ĐỊNH TUYẾN (ROUTING) ---
        if target_type == 'ALL_RESIDENTS':
            # Lấy tất cả user có liên kết với Resident
            # (Giả định Resident có trường 'user' hoặc User có related name 'resident')
            users = User.objects.filter(resident__isnull=False).distinct()
            
        elif target_type == 'BLOCK':
            # identifier = Building ID hoặc Code
            # Tìm Resident -> Apartment -> Building
            if identifier:
                users = User.objects.filter(
                    resident__current_apartment__building__id=identifier
                ).distinct()

        elif target_type == 'FLOOR':
            # identifier = "BuildingID-FloorNumber" (VD: "1-5" là Tòa 1 Tầng 5)
            if identifier and '-' in str(identifier):
                try:
                    build_id, floor_num = str(identifier).split('-')
                    users = User.objects.filter(
                        resident__current_apartment__building__id=build_id,
                        resident__current_apartment__floor_number=floor_num
                    ).distinct()
                except ValueError:
                    pass # Log lỗi format sai
                    
        elif target_type == 'SPECIFIC_UNITS':
            # identifier = List ID căn hộ (VD: "1,2,3")
            if identifier:
                unit_ids = str(identifier).split(',')
                users = User.objects.filter(
                    resident__current_apartment__id__in=unit_ids
                ).distinct()

        elif target_type == 'INTERNAL_GROUP':
            # identifier = Group ID (Tổ bảo vệ, Vệ sinh...)
            if identifier:
                users = User.objects.filter(groups__id=identifier).distinct()

        elif target_type == 'SPECIFIC_USERS':
             # identifier = List User ID
             if identifier:
                user_ids = str(identifier).split(',')
                users = User.objects.filter(id__in=user_ids)

        # --- BULK CREATE (TỐI ƯU HIỆU NĂNG) ---
        # Thay vì insert từng dòng, ta insert 1 lần hàng nghìn dòng
        recipients_to_create = []
        for user in users:
            # Kiểm tra tránh trùng lặp nếu code chạy 2 lần
            if not NotificationRecipient.objects.filter(notification=notification, recipient=user).exists():
                recipients_to_create.append(
                    NotificationRecipient(notification=notification, recipient=user)
                )
        
        if recipients_to_create:
            NotificationRecipient.objects.bulk_create(recipients_to_create)
            return len(recipients_to_create)
        
        return 0

    @staticmethod
    def mark_as_read(user, notification_id):
        """
        Đánh dấu đã đọc cho 1 user
        """
        from django.utils import timezone
        try:
            recipient_record = NotificationRecipient.objects.get(
                notification_id=notification_id,
                recipient=user
            )
            if not recipient_record.is_read:
                recipient_record.is_read = True
                recipient_record.read_at = timezone.now()
                recipient_record.save()
                return True
        except NotificationRecipient.DoesNotExist:
            return False
        return False