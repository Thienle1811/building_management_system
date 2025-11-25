from django.test import TestCase
from django.db.utils import IntegrityError
from django.db.models import ProtectedError
from apps.buildings.models import Building, Apartment
from apps.residents.models import Resident

class ResidentModelTest(TestCase):
    def setUp(self):
        """
        Hàm này chạy trước mỗi bài test để chuẩn bị dữ liệu giả.
        """
        # 1. Tạo Tòa nhà giả
        self.building = Building.objects.create(
            name="Tòa Test A",
            address="123 Đường Test",
            total_floors=10
        )
        
        # 2. Tạo Căn hộ giả
        self.apartment = Apartment.objects.create(
            building=self.building,
            floor_number=1,
            apartment_code="T1-101",
            area_m2=50.5,
            status="OCCUPIED"
        )

    def test_create_resident_success(self):
        """Case 1: Tạo cư dân thành công với đầy đủ thông tin"""
        resident = Resident.objects.create(
            full_name="Nguyễn Văn Test",
            identity_card="123456789012",
            phone_number="0909123456",
            current_apartment=self.apartment,
            relationship_type="OWNER"
        )
        # Kiểm tra xem đã lưu vào DB chưa
        self.assertEqual(Resident.objects.count(), 1)
        self.assertEqual(resident.full_name, "Nguyễn Văn Test")
        print("\n✅ Test 1: Tạo cư dân OK")

    def test_soft_delete_resident(self):
        """Case 2: Kiểm tra chức năng xóa mềm (Soft Delete)"""
        resident = Resident.objects.create(
            full_name="Trần Thị Xóa",
            identity_card="999999999999",
            phone_number="0909123456",
            current_apartment=self.apartment
        )
        
        # Thực hiện xóa mềm
        resident.soft_delete()
        
        # Kiểm tra:
        # 1. Manager mặc định (objects) không được tìm thấy
        self.assertEqual(Resident.objects.count(), 0)
        
        # 2. Manager toàn bộ (all_objects) vẫn phải thấy
        self.assertEqual(Resident.all_objects.count(), 1)
        
        # 3. Trường deleted_at phải có dữ liệu
        resident.refresh_from_db() # Tải lại từ DB
        self.assertIsNotNone(resident.deleted_at)
        print("✅ Test 2: Soft Delete OK")

    def test_unique_identity_card(self):
        """Case 3: Kiểm tra không được trùng CCCD"""
        Resident.objects.create(
            full_name="Người 1",
            identity_card="SAME_ID_123",
            phone_number="0901",
            current_apartment=self.apartment
        )
        
        # Tạo người thứ 2 giống y hệt số CCCD -> Mong đợi lỗi IntegrityError
        with self.assertRaises(IntegrityError):
            Resident.objects.create(
                full_name="Người 2",
                identity_card="SAME_ID_123", # Trùng
                phone_number="0902",
                current_apartment=self.apartment
            )
        print("✅ Test 3: Chặn trùng CCCD OK")

    def test_protect_apartment_delete(self):
        """Case 4: Không cho phép xóa Căn hộ nếu còn Cư dân (on_delete=PROTECT)"""
        Resident.objects.create(
            full_name="Cư Dân Cứng Đầu",
            identity_card="PROTECT_123",
            phone_number="0901",
            current_apartment=self.apartment
        )
        
        # Cố tình xóa căn hộ -> Mong đợi lỗi ProtectedError
        with self.assertRaises(ProtectedError):
            self.apartment.delete()
            
        print("✅ Test 4: Bảo vệ dữ liệu Căn hộ OK")