from rest_framework import serializers
from .models import StaffProfile, ShiftConfig, StaffRoster
from .models import MaintenanceTask

class ShiftConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftConfig
        fields = '__all__'

class StaffProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = StaffProfile
        fields = ['id', 'full_name', 'team', 'phone_number']

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

class StaffRosterSerializer(serializers.ModelSerializer):
    # Các trường đặc biệt dành cho FullCalendar
    title = serializers.SerializerMethodField()
    start = serializers.SerializerMethodField()
    end = serializers.SerializerMethodField()
    color = serializers.CharField(source='shift.color_code', read_only=True)
    staff_name = serializers.CharField(source='staff.user.get_full_name', read_only=True)

    class Meta:
        model = StaffRoster
        fields = ['id', 'staff', 'shift', 'date', 'title', 'start', 'end', 'color', 'staff_name']

    def get_title(self, obj):
        # Hiển thị: "Tên NV (Tên Ca)"
        staff_name = obj.staff.user.get_full_name() or obj.staff.user.username
        return f"{staff_name} ({obj.shift.name})"

    def get_start(self, obj):
        # Format chuẩn ISO: YYYY-MM-DDTHH:MM:SS
        return f"{obj.date}T{obj.shift.start_time}"

    def get_end(self, obj):
        return f"{obj.date}T{obj.shift.end_time}"

class MaintenanceTaskSerializer(serializers.ModelSerializer):
    """Serializer hiển thị chi tiết công việc cho nhân viên"""
    feedback_title = serializers.CharField(source='feedback.title', read_only=True)
    feedback_content = serializers.CharField(source='feedback.content', read_only=True)
    apartment_code = serializers.CharField(source='feedback.apartment.apartment_code', read_only=True)
    category = serializers.CharField(source='feedback.category.name', read_only=True, default="Chung")
    
    class Meta:
        model = MaintenanceTask
        fields = [
            'id', 'code', 'status', 'assigned_at', 'started_at', 'completed_at',
            'feedback_title', 'feedback_content', 'apartment_code', 'category',
            'result_image', 'staff_note'
        ]

class TaskCompleteSerializer(serializers.ModelSerializer):
    """Serializer chuyên dùng để Báo cáo hoàn thành (Bắt buộc có ảnh)"""
    class Meta:
        model = MaintenanceTask
        fields = ['result_image', 'staff_note']
        extra_kwargs = {
            'result_image': {'required': True}, # Bắt buộc phải upload ảnh [cite: 76]
            'staff_note': {'required': True}
        }