from rest_framework import serializers
from .models import MeterReading, Invoice, InvoiceItem

# --- 1. GIỮ NGUYÊN CODE CŨ (Ghi điện nước) ---
class MeterReadingSerializer(serializers.ModelSerializer):
    apartment_code = serializers.CharField(source='apartment.apartment_code', read_only=True)
    floor = serializers.IntegerField(source='apartment.floor_number', read_only=True)
    building_name = serializers.CharField(source='apartment.building.name', read_only=True)

    class Meta:
        model = MeterReading
        fields = [
            'id', 'apartment', 'apartment_code', 'building_name', 'floor',
            'service_type', 'record_month', 'record_year',
            'old_index', 'new_index', 'consumption', 'image_evidence', 
            'status', 'note'
        ]
        read_only_fields = ['old_index', 'consumption', 'status', 'record_month', 'record_year']

    def validate(self, data):
        new_index = data.get('new_index')
        instance = self.instance 
        if instance and new_index is not None and new_index < instance.old_index:
            raise serializers.ValidationError({"new_index": "Chỉ số mới không được nhỏ hơn chỉ số cũ."})
        return data

# --- 2. CODE MỚI (Hóa đơn) ---
class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ['title', 'amount', 'description']

class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    period = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_code', 'title', 'period',
            'month', 'year', 'total_amount', 
            'status', 'status_display', 'due_date', 
            'items', 'payment_method', 'payment_date'
        ]

    def get_period(self, obj):
        return f"{obj.month}/{obj.year}"

class PaymentProofSerializer(serializers.ModelSerializer):
    """Serializer dùng để upload ảnh chuyển khoản (nếu cần sau này)"""
    class Meta:
        model = Invoice
        fields = ['payment_proof', 'payment_method', 'note']