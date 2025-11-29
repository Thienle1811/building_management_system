from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    # Format ngày giờ đẹp để hiển thị trên Mobile
    created_at_display = serializers.DateTimeField(source='created_at', format="%H:%M %d/%m/%Y", read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 
            'title', 
            'body', 
            'notification_type', 
            'is_read', 
            'created_at', 
            'created_at_display'
        ]