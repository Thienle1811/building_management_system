from rest_framework import serializers
from .models import MeterReading, Invoice, InvoiceItem

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

class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ['title', 'amount', 'description']

class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    # Tạo trường ảo cho Mobile App
    title = serializers.SerializerMethodField()
    period = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            'id', 'code', 'title', 'period', 'month', 'year', 'total_amount', 
            'status', 'status_display', 'due_date', 'items', 'payment_proof',
            'payment_method', 'payment_date'
        ]

    def get_title(self, obj):
        # Tự động sinh tiêu đề: "Hóa đơn T12/2025"
        return f"Hóa đơn T{obj.month}/{obj.year}"

    def get_period(self, obj):
        return f"{obj.month}/{obj.year}"

class PaymentProofSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['payment_proof', 'payment_method', 'note']
        extra_kwargs = {
            'payment_proof': {'required': True},
            'payment_method': {'required': True}
        }