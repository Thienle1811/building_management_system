from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.buildings.models import Building, Apartment
from apps.residents.models import Resident
from apps.feedback.models import Feedback, FeedbackCategory, FeedbackStatusHistory

User = get_user_model()

class FeedbackBaseTest(TestCase):
    def setUp(self):
        # 1. Tạo dữ liệu nền (Tòa, Căn, User, Resident)
        self.building = Building.objects.create(name="Tòa Test", total_floors=5, address="HCM")
        self.apartment = Apartment.objects.create(
            building=self.building, floor_number=1, apartment_code="F01", 
            net_area=50, status="OCCUPIED"
        )
        
        # User đóng vai Cư dân
        self.user = User.objects.create_user(username="0909123123", password="123")
        self.resident = Resident.objects.create(
            full_name="Cư Dân A", phone_number="0909123123", 
            identity_card="111", current_apartment=self.apartment
        )
        
        # User đóng vai Admin
        self.admin_user = User.objects.create_superuser(username="admin", password="123")
        
        # Danh mục mẫu
        self.category = FeedbackCategory.objects.create(code="TEST_CAT", name="Test Category")

class FeedbackModelTest(FeedbackBaseTest):
    def test_create_feedback(self):
        """Test tạo model Feedback cơ bản"""
        fb = Feedback.objects.create(
            resident=self.resident,
            apartment=self.apartment,
            category=self.category,
            title="Hư đèn",
            description="Đèn hành lang tắt"
        )
        self.assertTrue(fb.code.startswith("FB-"))
        self.assertEqual(fb.status, "PENDING")
        print("\n✅ Test 1: Model Feedback Create OK")

class FeedbackAPITest(FeedbackBaseTest):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url_list = '/api/v1/feedback/list/'

    def test_create_feedback_via_api(self):
        """Test API gửi phản hồi từ Mobile"""
        data = {
            'category': self.category.id,
            'title': 'Mất nước',
            'description': 'Không có nước từ sáng',
            'priority': 'HIGH'
        }
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Feedback.objects.count(), 1)
        
        fb = Feedback.objects.first()
        self.assertEqual(fb.title, 'Mất nước')
        self.assertEqual(fb.resident, self.resident) # Phải tự gán đúng resident
        print("✅ Test 2: API Create Feedback OK")

    def test_list_feedback_privacy(self):
        """Test API chỉ trả về phản hồi của chính mình"""
        # Tạo 1 phản hồi của Resident A (mình)
        Feedback.objects.create(resident=self.resident, apartment=self.apartment, category=self.category, title="Của A")
        
        # Tạo 1 phản hồi của Resident B (người khác)
        res_b = Resident.objects.create(full_name="B", phone_number="0909456456", identity_card="222", current_apartment=self.apartment)
        Feedback.objects.create(resident=res_b, apartment=self.apartment, category=self.category, title="Của B")
        
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) # Chỉ thấy 1 cái
        self.assertEqual(response.data[0]['title'], "Của A")
        print("✅ Test 3: API Privacy OK")

class FeedbackWebTest(FeedbackBaseTest):
    def setUp(self):
        super().setUp()
        self.client = Client()
        self.client.force_login(self.admin_user)
        self.feedback = Feedback.objects.create(
            resident=self.resident, apartment=self.apartment, category=self.category,
            title="Test Web", status="PENDING"
        )
        self.url_detail = reverse('feedback_detail', args=[self.feedback.id])

    def test_update_status(self):
        """Test Admin cập nhật trạng thái -> Phải lưu lịch sử"""
        response = self.client.post(self.url_detail, {
            'status': 'PROCESSING',
            'note': 'Đang cho kỹ thuật kiểm tra'
        }, follow=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Kiểm tra trạng thái mới
        self.feedback.refresh_from_db()
        self.assertEqual(self.feedback.status, 'PROCESSING')
        self.assertEqual(self.feedback.internal_note, 'Đang cho kỹ thuật kiểm tra')
        
        # Kiểm tra lịch sử (History)
        history = FeedbackStatusHistory.objects.filter(feedback=self.feedback).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.old_status, 'PENDING')
        self.assertEqual(history.new_status, 'PROCESSING')
        self.assertEqual(history.changed_by, self.admin_user)
        print("✅ Test 4: Web Update Status & History OK")