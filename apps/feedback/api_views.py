import logging
from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Feedback, FeedbackCategory
from .serializers import FeedbackSerializer, FeedbackCategorySerializer
from apps.residents.models import Resident

# Tạo logger
logger = logging.getLogger(__name__)

class FeedbackCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """API lấy danh mục phản hồi (Public cho user đã login)"""
    queryset = FeedbackCategory.objects.all()
    serializer_class = FeedbackCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class FeedbackViewSet(viewsets.ModelViewSet):
    """API Phản hồi cho Mobile App"""
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Chỉ trả về phản hồi của chính cư dân đó"""
        user = self.request.user
        try:
            resident = Resident.objects.get(phone_number=user.username)
            return Feedback.objects.filter(resident=resident).order_by('-created_at')
        except Resident.DoesNotExist:
            return Feedback.objects.none()

    def perform_create(self, serializer):
        """Tự động gán Resident và Apartment khi tạo"""
        user = self.request.user
        try:
            resident = Resident.objects.get(phone_number=user.username)
            
            if not resident.current_apartment:
                 logger.warning(f"PMS-04: User {user.username} cố tạo FB nhưng chưa có căn hộ.")
                 raise PermissionDenied("Cư dân chưa được gán vào căn hộ nào.")
            
            # Lưu phản hồi
            feedback = serializer.save(resident=resident, apartment=resident.current_apartment)
            
            # --- LOGGING ---
            logger.info(f"PMS-04: Mobile User {user.username} đã gửi phản hồi mới: {feedback.code} - {feedback.title}")
            # ---------------
            
        except Resident.DoesNotExist:
            logger.error(f"PMS-04: User {user.username} không tìm thấy thông tin Resident.")
            raise PermissionDenied("Tài khoản này chưa được liên kết với thông tin Cư dân.")