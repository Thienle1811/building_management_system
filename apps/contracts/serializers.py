from rest_framework import serializers
from .models import Contract
from apps.buildings.serializers import ApartmentSerializer

class ContractSerializer(serializers.ModelSerializer):
    # Nhúng thông tin căn hộ chi tiết để hiển thị trên App (nếu cần)
    # apartment_info = ApartmentSerializer(source='apartment', read_only=True)
    
    # Format lại tên loại hợp đồng và trạng thái để hiển thị tiếng Việt thay vì mã code
    contract_type_display = serializers.CharField(source='get_contract_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # URL file hợp đồng đầy đủ
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = [
            'id', 
            'code', 
            'contract_type', 'contract_type_display',
            'status', 'status_display',
            'start_date', 'end_date',
            'deposit_amount',
            'file_url',  # Link tải file
            'created_at'
        ]

    def get_file_url(self, obj):
        """Trả về đường dẫn file đầy đủ (có domain)"""
        if obj.contract_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.contract_file.url)
            return obj.contract_file.url
        return None