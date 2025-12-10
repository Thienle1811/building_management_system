from django import forms
from .models import Resident, Vehicle

class ResidentForm(forms.ModelForm):
    class Meta:
        model = Resident
        fields = [
            'full_name', 'identity_card', 'phone_number', 
            'current_apartment', 'relationship_type', 
            'emergency_phone', 'identity_card_image_front', 'identity_card_image_back'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: Nguyễn Văn A'}),
            'identity_card': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số CCCD/CMND'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số điện thoại'}),
            'current_apartment': forms.Select(attrs={'class': 'form-select'}), # Dropdown chọn căn hộ
            'relationship_type': forms.Select(attrs={'class': 'form-select'}),
            'emergency_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'identity_card_image_front': forms.FileInput(attrs={'class': 'form-control'}),
            'identity_card_image_back': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'full_name': 'Họ và Tên',
            'current_apartment': 'Căn hộ',
            'relationship_type': 'Vai trò',
            # Các label khác Django tự lấy từ verbose_name trong Model
        }

# Form nhập xe (Sẽ dùng formset để nhập nhiều xe cùng lúc)
class VehicleForm(forms.ModelForm):
    """Form quản lý phương tiện"""
    class Meta:
        model = Vehicle
        fields = ['resident', 'vehicle_type', 'license_plate', 'manufacturer', 'model', 'color']
        widgets = {
            'resident': forms.Select(attrs={'class': 'form-select select2'}), # select2 để tìm tên cư dân cho nhanh
            'vehicle_type': forms.Select(attrs={'class': 'form-select'}),
            'license_plate': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: 59A-123.45', 'style': 'text-transform: uppercase;'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: Honda, Toyota'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: SH 150i, Vios'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
        }