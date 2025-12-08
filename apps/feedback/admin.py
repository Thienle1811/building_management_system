from django.contrib import admin
from .models import Feedback, FeedbackCategory, FeedbackStatusHistory
# Import Service gửi thông báo
from apps.notifications.services import NotificationService

@admin.register(FeedbackCategory)
class FeedbackCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_default')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'resident', 'category', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('code', 'title', 'resident__username', 'resident__full_name')
    readonly_fields = ('code', 'created_at', 'updated_at')

    # --- HÀM QUAN TRỌNG: Gửi thông báo khi Admin bấm Save ---
    def save_model(self, request, obj, form, change):
        """
        Hàm này chạy tự động khi bạn bấm nút SAVE trong Admin
        """
        if change: # Chỉ chạy khi là hành động Sửa (không phải Tạo mới)
            try:
                # 1. Lấy trạng thái cũ từ Database trước khi lưu cái mới
                old_feedback = Feedback.objects.get(pk=obj.pk)
                old_status = old_feedback.status
                new_status = obj.status

                # 2. Lưu dữ liệu mới xuống DB
                super().save_model(request, obj, form, change)

                # 3. Kiểm tra nếu trạng thái thay đổi thì gửi thông báo
                if old_status != new_status:
                    print(f"⚡ [ADMIN] Phát hiện đổi trạng thái: {old_status} -> {new_status}")
                    NotificationService.send_feedback_notification(obj, old_status, new_status)
                else:
                    print("⚠️ [ADMIN] Trạng thái không đổi, không gửi thông báo.")

            except Feedback.DoesNotExist:
                super().save_model(request, obj, form, change)
        else:
            # Trường hợp tạo mới
            super().save_model(request, obj, form, change)

@admin.register(FeedbackStatusHistory)
class FeedbackStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('feedback', 'old_status', 'new_status', 'changed_by', 'created_at')
    readonly_fields = ('created_at',)