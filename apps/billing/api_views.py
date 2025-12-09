from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import MeterReading, Invoice
from .serializers import MeterReadingSerializer, InvoiceSerializer, PaymentProofSerializer

class MeterReadingViewSet(viewsets.ModelViewSet):
    """
    API dành cho Bảo vệ đi ghi số Điện/Nước
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MeterReadingSerializer
    
    def get_queryset(self):
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        status_param = self.request.query_params.get('status')
        queryset = MeterReading.objects.all().order_by('apartment__floor_number')
        
        if month and year: 
            queryset = queryset.filter(record_month=month, record_year=year)
        if status_param: 
            queryset = queryset.filter(status=status_param)
        return queryset

    def perform_update(self, serializer):
        # Khi bảo vệ update số, tự động đổi trạng thái thành RECORDED
        serializer.save(status='RECORDED')

class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API cho Cư dân xem hóa đơn và thanh toán
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        user = self.request.user
        
        # --- LOGIC MỚI CẬP NHẬT ---
        # 1. Nếu là Admin/Staff: Cho phép xem TẤT CẢ (bao gồm cả DRAFT) để test
        if user.is_staff:
            return Invoice.objects.all().order_by('-year', '-month')

        # 2. Nếu là Cư dân: Chỉ xem hóa đơn của căn hộ mình đang ở
        # VÀ Không hiển thị hóa đơn nháp (DRAFT)
        if hasattr(user, 'resident') and user.resident.current_apartment:
            return Invoice.objects.filter(
                apartment=user.resident.current_apartment
            ).exclude(status='DRAFT').order_by('-year', '-month')
            
        return Invoice.objects.none()

    @action(detail=True, methods=['post'], serializer_class=PaymentProofSerializer)
    def upload_proof(self, request, pk=None):
        """
        API: POST /api/v1/billing/invoices/{id}/upload_proof/
        Cư dân gửi ảnh chuyển khoản.
        """
        invoice = self.get_object()
        
        # Chỉ cho phép upload nếu chưa thanh toán
        if invoice.status == 'PAID':
            return Response({'detail': 'Hóa đơn này đã được thanh toán rồi.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PaymentProofSerializer(invoice, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(
                payment_date=timezone.now(),
                # Giữ nguyên trạng thái để Admin duyệt, hoặc đổi sang 'PENDING_REVIEW' tùy logic
            )
            return Response({'status': 'Uploaded successfully', 'data': serializer.data})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)