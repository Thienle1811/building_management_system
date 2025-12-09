from django import forms
from .models import Notification

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = [
            'title', 'content', 'notification_type', 'priority',
            'target_type', 'target_identifier', 'file', 'scheduled_at'
        ]
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
            'scheduled_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        help_texts = {
            'target_identifier': 'Nhập ID Tòa nhà, Số tầng hoặc để trống nếu chọn "Toàn bộ cư dân"',
        }