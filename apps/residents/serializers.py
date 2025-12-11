from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Resident, Vehicle

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'license_plate', 'vehicle_type', 'manufacturer', 'model', 'color']

class ResidentSerializer(serializers.ModelSerializer):
    apartment_code = serializers.CharField(source='current_apartment.apartment_code', read_only=True)
    
    class Meta:
        model = Resident
        fields = ['id', 'full_name', 'phone_number', 'identity_card', 'apartment_code', 'relationship_type']

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Mật khẩu mới không khớp.")
        return data