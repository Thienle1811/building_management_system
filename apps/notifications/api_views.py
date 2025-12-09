from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Notification
from .serializers import NotificationReadSerializer, NotificationWriteSerializer
from .services import NotificationService

class NotificationViewSet(viewsets.ModelViewSet):
    """
    API Quản lý thông báo cho Mobile App
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return NotificationWriteSerializer
        return NotificationReadSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Notification.objects.all().order_by('-created_at')
        
        # Cư dân chỉ xem tin của mình
        return Notification.objects.filter(recipients__recipient=user).order_by('-created_at')

    def perform_create(self, serializer):
        """
        Xử lý khi tạo thông báo qua API (Thường dùng cho Admin thao tác trên App quản lý)
        """
        # Lấy thời gian hẹn từ dữ liệu gửi lên
        scheduled_at = serializer.validated_data.get('scheduled_at')
        now = timezone.now()
        
        is_sending_now = True
        
        # --- LOGIC HẸN GIỜ (PHASE 4) ---
        if scheduled_at and scheduled_at > now:
            is_sending_now = False
        
        if is_sending_now:
            notification = serializer.save(is_sent=True, sent_at=now)
        else:
            notification = serializer.save(is_sent=False)
            
        # Tạo danh sách người nhận
        count = NotificationService.create_notification_recipients(notification)
        
        # Log để debug
        status_text = "Gửi ngay" if is_sending_now else f"Hẹn giờ ({scheduled_at})"
        print(f"API: Đã tạo thông báo [{status_text}] cho {count} người.")

    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        """Đánh dấu đã đọc 1 tin"""
        success = NotificationService.mark_as_read(request.user, pk)
        if success:
            return Response({'status': 'marked as read'}, status=status.HTTP_200_OK)
        return Response({'status': 'failed', 'detail': 'Not found or already read'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        """Lấy số lượng tin chưa đọc"""
        count = Notification.objects.filter(
            recipients__recipient=request.user,
            recipients__is_read=False
        ).count()
        return Response({'unread_count': count})