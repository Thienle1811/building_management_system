from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Resident
from .serializers import ResidentSerializer

class ResidentViewSet(viewsets.ModelViewSet):
    """
    API CRUD Cư dân:
    - GET /api/residents/: Lấy danh sách
    - POST /api/residents/: Tạo mới
    - GET /api/residents/{id}/: Xem chi tiết
    - DELETE /api/residents/{id}/: Xóa mềm
    """
    queryset = Resident.objects.all().select_related('current_apartment')
    serializer_class = ResidentSerializer
    
    # Cấu hình bộ lọc và tìm kiếm
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['current_apartment', 'relationship_type'] # Lọc theo căn hộ, vai trò
    search_fields = ['full_name', 'identity_card', 'phone_number'] # Tìm theo tên, CCCD, SĐT

    def destroy(self, request, *args, **kwargs):
        """Ghi đè hàm xóa để thực hiện Soft Delete"""
        instance = self.get_object()
        instance.soft_delete() # Gọi hàm soft_delete chúng ta viết ở utils.py
        return Response(status=status.HTTP_204_NO_CONTENT)