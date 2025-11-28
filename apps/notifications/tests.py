from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime
from unittest.mock import patch
from apps.buildings.models import Apartment, Building
from apps.residents.models import Resident
from apps.feedback.models import Feedback, FeedbackCategory
from apps.notifications.services import NotificationService
from apps.notifications.models import Notification

User = get_user_model()

class NotificationServiceTest(TestCase):
    def setUp(self):
        # Tạo dữ liệu nền
        self.user = User.objects.create_user(username="0909123456", password="123")
        self.building = Building.objects.create(name="Tòa Noti", total_floors=5, address="HN")
        self.apartment = Apartment.objects.create(
            building=self.building, floor_number=1, apartment_code="N01", 
            net_area=50, status="OCCUPIED"
        )
        self.resident = Resident.objects.create(
            full_name="User Noti", phone_number="0909123456", 
            identity_card="999", current_apartment=self.apartment
        )
        self.category = FeedbackCategory.objects.create(code="TEST", name="Test")
        self.feedback = Feedback.objects.create(
            resident=self.resident, apartment=self.apartment, category=self.category,
            title="Test FB", status="PENDING"
        )

    def test_send_notification_immediate(self):
        """Test gửi ngay vào giờ hành chính (VD: 10:00 sáng)"""
        # Mock thời gian là 10h sáng
        mock_now = datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.get_current_timezone())
        
        with patch('django.utils.timezone.now', return_value=mock_now):
            with patch('django.utils.timezone.localtime', return_value=mock_now):
                NotificationService.send_feedback_notification(self.feedback, 'PENDING', 'PROCESSING')
                
                # Kiểm tra DB
                noti = Notification.objects.first()
                self.assertIsNotNone(noti)
                self.assertTrue(noti.is_sent) # Phải gửi ngay
                self.assertEqual(noti.title, "Phản hồi đang được xử lý")

    def test_send_notification_quiet_hours(self):
        """Test gửi vào giờ yên lặng (VD: 23:30 đêm) -> Phải xếp hàng"""
        # Mock thời gian là 23h30
        mock_now = datetime(2025, 1, 1, 23, 30, 0, tzinfo=timezone.get_current_timezone())
        
        with patch('django.utils.timezone.now', return_value=mock_now):
            with patch('django.utils.timezone.localtime', return_value=mock_now):
                NotificationService.send_feedback_notification(self.feedback, 'PROCESSING', 'DONE')
                
                noti = Notification.objects.first()
                self.assertFalse(noti.is_sent) # Chưa được gửi
                # Thời gian gửi phải là 6:30 sáng hôm sau (ngày 2)
                self.assertEqual(noti.scheduled_at.hour, 6)
                self.assertEqual(noti.scheduled_at.minute, 30)
                self.assertEqual(noti.scheduled_at.day, 2)