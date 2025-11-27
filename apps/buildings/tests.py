import io
import pandas as pd
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.buildings.models import Building, Apartment

class BuildingModelTest(TestCase):
    def test_generate_apartments(self):
        """Test chức năng tự sinh căn hộ (Skeleton)"""
        # 1. Tạo tòa nhà 5 tầng, mỗi tầng 4 căn
        building = Building.objects.create(
            name="Tòa Test Auto", 
            code="AUTO", 
            total_floors=5, 
            units_per_floor_default=4
        )
        
        # 2. Gọi hàm sinh
        count = building.generate_apartments()
        
        # 3. Kiểm tra kết quả: Tổng số căn phải là 5 * 4 = 20
        self.assertEqual(count, 20)
        self.assertEqual(Apartment.objects.count(), 20)
        self.assertTrue(Apartment.objects.filter(apartment_code="AUTO-01.01").exists())
        self.assertTrue(Apartment.objects.filter(apartment_code="AUTO-05.04").exists())
        print("\n✅ Test 1: Generate Apartments OK")

class ApartmentSearchTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.building = Building.objects.create(name="Tòa Search", total_floors=10)
        
        # Tạo dữ liệu mẫu
        Apartment.objects.create(
            building=self.building, floor_number=1, unit_number="01", apartment_code="S-01", 
            net_area=50, price=1500000000, direction="EAST", room_type="1PN"
        )
        Apartment.objects.create(
            building=self.building, floor_number=2, unit_number="02", apartment_code="S-02", 
            net_area=80, price=3000000000, direction="SE", room_type="2PN"
        )
        Apartment.objects.create(
            building=self.building, floor_number=3, unit_number="03", apartment_code="S-03", 
            net_area=100, price=5000000000, direction="NW", room_type="3PN"
        )

    def test_search_filter(self):
        """Test bộ lọc tìm kiếm"""
        url = reverse('apartment_search')
        
        # Case 1: Lọc theo diện tích (50-90m2) -> Mong đợi 2 căn (S-01, S-02)
        response = self.client.get(url, {'min_area': 50, 'max_area': 90})
        self.assertEqual(len(response.context['apartments']), 2)
        
        # Case 2: Lọc theo hướng (Đông Nam - SE) -> Mong đợi 1 căn (S-02)
        response = self.client.get(url, {'direction': 'SE'})
        self.assertEqual(len(response.context['apartments']), 1)
        self.assertEqual(response.context['apartments'][0].apartment_code, "S-02")
        
        # Case 3: Lọc theo giá (> 4 tỷ) -> Mong đợi 1 căn (S-03)
        response = self.client.get(url, {'min_price': 4000000000})
        self.assertEqual(len(response.context['apartments']), 1)
        self.assertEqual(response.context['apartments'][0].apartment_code, "S-03")
        
        print("✅ Test 2: Search Filter OK")

class ApartmentImportTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.building = Building.objects.create(name="Tòa Import", code="IMP", total_floors=10)
        self.url = reverse('apartment_import')

    def test_import_excel(self):
        """Test import file Excel"""
        # 1. Tạo file Excel giả lập bằng Pandas
        data = {
            'code': ['IMP-01.01', 'IMP-01.02'],
            'floor': [1, 1],
            'unit': ['01', '02'],
            'net_area': [60.5, 75.0],
            'type': ['2PN', '2PN'],
            'price': [2000000000, 2500000000],
            'direction': ['EAST', 'WEST']
        }
        df = pd.DataFrame(data)
        
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        
        excel_file = SimpleUploadedFile(
            "test_import.xlsx", 
            excel_buffer.read(), 
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # 2. Gửi POST request
        response = self.client.post(self.url, {
            'building': self.building.id,
            'excel_file': excel_file
        }, follow=True)

        # 3. Kiểm tra kết quả
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Apartment.objects.count(), 2)
        
        apt1 = Apartment.objects.get(apartment_code='IMP-01.01')
        self.assertEqual(float(apt1.net_area), 60.5)
        self.assertEqual(apt1.direction, 'EAST')
        
        print("✅ Test 3: Import Excel OK")