from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Contract
from .serializers import ContractSerializer
from apps.residents.models import Resident

class MobileContractViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API dành cho Mobile App: Chỉ xem (Read-only)
    Endpoint: /api/v1/mobile/contracts/
    """
    serializer_class = ContractSerializer
    # Chỉ cho phép user đã đăng nhập truy cập
    permission_classes = [permissions.IsAuthenticated] 

    def get_queryset(self):
        """
        Lọc hợp đồng theo Cư dân đang đăng nhập.
        Logic: 
        1. Lấy thông tin Resident gắn với User đang login.
        2. Kiểm tra nếu là Chủ hộ (OWNER) -> Trả về danh sách hợp đồng.
        3. Nếu không phải -> Trả về rỗng.
        """
        user = self.request.user
        
        # Giả sử User model có liên kết tới Resident (hoặc ta query ngược lại)
        # Tùy vào cách bạn thiết kế User authentication, đoạn này có thể cần điều chỉnh.
        # Ở đây ta giả định 1 User gắn với 1 Resident qua email hoặc phone.
        try:
            # Tìm Resident có phone hoặc email trùng với User
            resident = Resident.objects.filter(phone_number=user.username).first() 
            # (Lưu ý: Logic này phụ thuộc vào cách bạn làm Login User)
            
            if resident and resident.relationship_type == 'OWNER':
                # Lấy tất cả hợp đồng mà cư dân này đứng tên
                return Contract.objects.filter(resident=resident).order_by('-start_date')
            else:
                # Không phải chủ hộ hoặc không tìm thấy cư dân -> Trả về rỗng
                return Contract.objects.none()
        except Exception:
            return Contract.objects.none()

    @action(detail=False, methods=['get'])
    def current(self, request):
        """
        API phụ: Lấy hợp đồng đang hiệu lực (ACTIVE) của căn hộ hiện tại
        GET /api/v1/mobile/contracts/current/
        """
        queryset = self.get_queryset().filter(status='ACTIVE')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)