from rest_framework import serializers
from .models import Notification, NotificationRecipient

class NotificationReadSerializer(serializers.ModelSerializer):
    """
    Serializer dùng để hiển thị danh sách thông báo cho Cư Dân.
    Có thêm trường 'is_read' được lấy từ bảng trung gian.
    """
    is_read = serializers.SerializerMethodField()
    created_at_formatted = serializers.DateTimeField(source='created_at', format="%d/%m/%Y %H:%M", read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'content', 'notification_type', 'priority', 
            'file', 'created_at_formatted', 'is_read'
        ]

    def get_is_read(self, obj):
        # Lấy user từ context request (được truyền từ View)
        user = self.context.get('request').user
        if user.is_authenticated:
            # Tìm record trong bảng trung gian
            # (Dùng filter().first() an toàn hơn get() trong serializer)
            recipient = obj.recipients.filter(recipient=user).first()
            if recipient:
                return recipient.is_read
        return False

class NotificationWriteSerializer(serializers.ModelSerializer):
    """
    Serializer dùng cho Admin tạo thông báo mới.
    """
    class Meta:
        model = Notification
        fields = [
            'title', 'content', 'notification_type', 'priority', 
            'target_type', 'target_identifier', 'file', 'scheduled_at'
        ]
        
    def validate(self, data):
        # Kiểm tra logic: Nếu chọn gửi theo Block thì phải có ID Block
        if data.get('target_type') == 'BLOCK' and not data.get('target_identifier'):
            raise serializers.ValidationError({"target_identifier": "Vui lòng chọn Tòa nhà."})
        return data