from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date
from django.core.exceptions import ValidationError
from apps.buildings.models import Building, Apartment
from apps.residents.models import Resident
from apps.contracts.models import Contract

class ContractModelTest(TestCase):
    def setUp(self):
        self.building = Building.objects.create(name="Tòa Test", total_floors=5)
        
        self.apartment = Apartment.objects.create(
            building=self.building, 
            apartment_code="P101", 
            floor_number=1, 
            area_m2=50.0,
            status="OCCUPIED"
        )
        
        self.resident = Resident.objects.create(
            full_name="Nguyễn Văn Chủ Hộ",
            identity_card="111111111", # <--- Đã thêm
            phone_number="0909123456",
            current_apartment=self.apartment,
            relationship_type="OWNER"
        )

    def test_end_date_validation(self):
        """Test validation: Ngày kết thúc không được nhỏ hơn ngày bắt đầu"""
        contract = Contract(
            code="HD-ERROR-DATE",
            apartment=self.apartment,
            resident=self.resident,
            start_date=date(2025, 1, 1),
            end_date=date(2024, 1, 1) # Sai logic
        )
        # Bây giờ Model đã có hàm clean(), lệnh này sẽ bắt được lỗi
        with self.assertRaises(ValidationError):
            contract.full_clean()

class ContractAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.building = Building.objects.create(name="Tòa API", total_floors=5)
        
        self.apartment = Apartment.objects.create(
            building=self.building, 
            apartment_code="A202", 
            floor_number=2,
            area_m2=65.5,
            status="OCCUPIED"
        )
        
        # 2. Tạo User & Resident (CHỦ HỘ)
        self.owner_user = User.objects.create_user(username="0909888888", password="password123")
        self.owner_resident = Resident.objects.create(
            full_name="Chủ Hộ A",
            identity_card="222222222", # <--- Đã thêm (Khác người dưới)
            phone_number="0909888888", 
            current_apartment=self.apartment,
            relationship_type="OWNER"
        )
        
        # 3. Tạo User & Resident (KHÁCH THUÊ)
        self.tenant_user = User.objects.create_user(username="0909777777", password="password123")
        self.tenant_resident = Resident.objects.create(
            full_name="Khách Thuê B",
            identity_card="333333333", # <--- Đã thêm (Khác người trên)
            phone_number="0909777777",
            current_apartment=self.apartment,
            relationship_type="TENANT"
        )

        # 4. Tạo Hợp đồng cho Chủ hộ
        self.contract = Contract.objects.create(
            code="HD-API-TEST",
            apartment=self.apartment,
            resident=self.owner_resident,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            status="ACTIVE"
        )

    def test_api_owner_can_view_contracts(self):
        """Case 1: Chủ hộ đăng nhập -> Thấy hợp đồng"""
        self.client.force_authenticate(user=self.owner_user)
        response = self.client.get('/api/v1/mobile/contracts/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['code'], "HD-API-TEST")

    def test_api_tenant_cannot_view_contracts(self):
        """Case 2: Khách thuê đăng nhập -> Không thấy hợp đồng (Mảng rỗng)"""
        self.client.force_authenticate(user=self.tenant_user)
        response = self.client.get('/api/v1/mobile/contracts/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_api_anonymous_user(self):
        """Case 3: Không đăng nhập -> Lỗi 403 Forbidden"""
        response = self.client.get('/api/v1/mobile/contracts/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)