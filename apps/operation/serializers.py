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
        # SỬA LỖI: Đổi 'phone_number' thành 'phone'
        fields = ['id', 'full_name', 'team', 'phone']

    def get_full_name(self, obj):
        if obj.user:
            return obj.user.get_full_name() or obj.user.username
        return "Unknown"

class StaffRosterSerializer(serializers.ModelSerializer):
    # Các trường đặc biệt dành cho FullCalendar
    title = serializers.SerializerMethodField()
    start = serializers.SerializerMethodField()
    end = serializers.SerializerMethodField()
    # SỬA LỖI: Bỏ 'color_code' vì model không có, gán màu cứng hoặc logic khác
    color = serializers.SerializerMethodField() 
    staff_name = serializers.CharField(source='staff.user.get_full_name', read_only=True)

    class Meta:
        model = StaffRoster
        fields = ['id', 'staff', 'shift', 'date', 'title', 'start', 'end', 'color', 'staff_name']

    def get_title(self, obj):
        staff_name = obj.staff.user.get_full_name() or obj.staff.user.username
        return f"{staff_name} ({obj.shift.name})"

    def get_start(self, obj):
        return f"{obj.date}T{obj.shift.start_time}"

    def get_end(self, obj):
        return f"{obj.date}T{obj.shift.end_time}"
    
    def get_color(self, obj):
        # Tự động gán màu theo ca trực (Ví dụ: Sáng=Xanh, Chiều=Vàng...)
        if 'Sáng' in obj.shift.name: return '#0d6efd' # Blue
        if 'Chiều' in obj.shift.name: return '#ffc107' # Warning
        if 'Đêm' in obj.shift.name: return '#212529'  # Dark
        return '#6c757d' # Grey default

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
    """Serializer chuyên dùng để Báo cáo hoàn thành"""
    class Meta:
        model = MaintenanceTask
        fields = ['result_image', 'staff_note']
        extra_kwargs = {
            'result_image': {'required': True},
            'staff_note': {'required': True}
        }