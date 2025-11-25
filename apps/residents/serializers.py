from rest_framework import serializers
from .models import Resident, Vehicle

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'license_plate', 'vehicle_type']

class ResidentSerializer(serializers.ModelSerializer):
    # Nhúng danh sách xe vào trong thông tin cư dân
    vehicles = VehicleSerializer(many=True, required=False)
    
    # Hiển thị mã căn hộ thay vì chỉ hiện ID số
    apartment_code = serializers.CharField(source='current_apartment.apartment_code', read_only=True)

    class Meta:
        model = Resident
        fields = [
            'id', 'full_name', 'identity_card', 'phone_number', 
            'current_apartment', 'apartment_code', 'relationship_type',
            'identity_card_image_front', 'identity_card_image_back',
            'vehicles', 'created_at'
        ]

    def create(self, validated_data):
        # Logic để lưu xe khi tạo cư dân
        vehicles_data = validated_data.pop('vehicles', [])
        resident = Resident.objects.create(**validated_data)
        
        for vehicle_data in vehicles_data:
            Vehicle.objects.create(resident=resident, **vehicle_data)
        return resident