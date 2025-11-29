from django import forms

class SystemNotificationForm(forms.Form):
    TARGET_CHOICES = (
        ('ALL', 'Gửi cho TẤT CẢ cư dân'),
        ('OWNERS', 'Chỉ gửi cho CHỦ HỘ'),
        # ('BLOCK_A', 'Chỉ gửi tòa A - Nâng cấp sau'),
    )

    title = forms.CharField(
        max_length=255, 
        label="Tiêu đề thông báo",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: Thông báo bảo trì thang máy'})
    )
    
    body = forms.CharField(
        label="Nội dung chi tiết",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Nhập nội dung thông báo...'})
    )
    
    target_group = forms.ChoiceField(
        label="Đối tượng nhận",
        choices=TARGET_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )