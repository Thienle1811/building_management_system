from rest_framework import serializers
from .models import Building, Apartment

class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ['id', 'name', 'address', 'total_floors']

class ApartmentSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source='building.name', read_only=True)

    class Meta:
        model = Apartment
        fields = ['id', 'apartment_code', 'building', 'building_name', 'floor_number', 'area_m2', 'status']