from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone

# Import đầy đủ các Models
from .models import StaffProfile, ShiftConfig, StaffRoster, MaintenanceTask

# Import đầy đủ các Serializers (Sửa lỗi tại đây)
from .serializers import (
    StaffProfileSerializer, 
    ShiftConfigSerializer, 
    StaffRosterSerializer,
    MaintenanceTaskSerializer, # <--- Đã thêm
    TaskCompleteSerializer     # <--- Đã thêm
)

class RosterAPIViewSet(viewsets.ModelViewSet):
    """API CRUD cho lịch trực (FullCalendar gọi vào đây)"""
    permission_classes = [IsAuthenticated]
    queryset = StaffRoster.objects.all()
    serializer_class = StaffRosterSerializer

    def create(self, request, *args, **kwargs):
        staff_id = request.data.get('staff')
        shift_id = request.data.get('shift')
        date = request.data.get('date')

        # 1. Kiểm tra trùng lặp: 1 người không làm cùng 1 ca trong 1 ngày
        if StaffRoster.objects.filter(staff_id=staff_id, shift_id=shift_id, date=date).exists():
            return Response(
                {"detail": "Cảnh báo: Nhân viên này đã có ca trực này trong ngày rồi!"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().create(request, *args, **kwargs)

class OperationMasterDataViewSet(viewsets.ViewSet):
    """API lấy danh sách Nhân viên & Ca trực để hiển thị Sidebar bên trái"""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        staffs = StaffProfile.objects.filter(status='ACTIVE')
        shifts = ShiftConfig.objects.filter(is_active=True)
        
        return Response({
            'staffs': StaffProfileSerializer(staffs, many=True).data,
            'shifts': ShiftConfigSerializer(shifts, many=True).data
        })

class StaffTaskViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API dành cho Nhân viên xem và xử lý công việc được giao.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MaintenanceTaskSerializer
    parser_classes = [MultiPartParser, FormParser] # Hỗ trợ upload ảnh

    def get_queryset(self):
        # Chỉ lấy các công việc được giao cho nhân viên đang đăng nhập
        user = self.request.user
        # Kiểm tra xem user có hồ sơ nhân viên không để tránh lỗi
        if hasattr(user, 'staff_profile'):
            return MaintenanceTask.objects.filter(staff=user.staff_profile).order_by('-assigned_at')
        return MaintenanceTask.objects.none()

    # ACTION 1: Nhận việc / Bắt đầu
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        task = self.get_object()
        
        if task.status != 'PENDING':
            return Response({'detail': 'Chỉ có thể bắt đầu công việc đang ở trạng thái Chờ.'}, status=status.HTTP_400_BAD_REQUEST)

        task.status = 'IN_PROGRESS'
        task.started_at = timezone.now()
        task.save()
        
        # Cập nhật luôn trạng thái Feedback gốc để cư dân biết
        if task.feedback:
            task.feedback.status = 'PROCESSING'
            task.feedback.save()

        return Response({'status': 'Task started', 'data': MaintenanceTaskSerializer(task).data})

    # ACTION 2: Hoàn thành & Gửi ảnh
    @action(detail=True, methods=['post'], serializer_class=TaskCompleteSerializer)
    def complete(self, request, pk=None):
        task = self.get_object()

        if task.status != 'IN_PROGRESS':
            return Response({'detail': 'Bạn phải Bắt đầu công việc trước khi Hoàn thành.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TaskCompleteSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(
                status='COMPLETED',
                completed_at=timezone.now()
            )
            
            # Cập nhật trạng thái Feedback gốc thành Đã xong
            if task.feedback:
                task.feedback.status = 'DONE' # Hoặc 'COMPLETED' tùy model Feedback
                task.feedback.save()

            return Response({'status': 'Task completed', 'data': MaintenanceTaskSerializer(task).data})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)