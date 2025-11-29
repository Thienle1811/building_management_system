from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer
from .models import Notification, NotificationDevice

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """API Thông báo dành cho Mobile App"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Chỉ lấy thông báo của user đang đăng nhập & đã được gửi đi
        return Notification.objects.filter(
            recipient=self.request.user, 
            is_sent=True
        ).order_by('-created_at')

    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        """API đánh dấu tất cả là đã đọc"""
        self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({'status': 'success', 'message': 'Đã đánh dấu tất cả là đã đọc'})

    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        """API đánh dấu 1 thông báo là đã đọc"""
        notification = self.get_object()
        if not notification.is_read:
            notification.is_read = True
            notification.save()
        return Response({'status': 'success'})
    @action(detail=False, methods=['post'], url_path='register-device')
    def register_device(self, request):
        """API đăng ký Expo Push Token từ Mobile"""
        token = request.data.get('expo_push_token')
        platform = request.data.get('platform')

        if not token:
            return Response({'error': 'Token is required'}, status=400)

        # Lưu hoặc cập nhật Token
        device, created = NotificationDevice.objects.update_or_create(
            expo_push_token=token,
            defaults={
                'user': request.user,
                'platform': platform
            }
        )
        return Response({'status': 'success', 'device_id': device.id})  