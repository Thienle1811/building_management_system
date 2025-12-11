from django import forms
from .models import Resident, Vehicle

class ResidentForm(forms.ModelForm):
    """Form quản lý cư dân (Web Admin)"""
    class Meta:
        model = Resident
        # Đã XÓA trường 'user' khỏi danh sách fields để ẩn đi
        fields = [
            'full_name', 'phone_number', 'identity_card', 
            'emergency_phone', 'current_apartment', 'relationship_type',
            'identity_card_image_front', 'identity_card_image_back'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nguyễn Văn A'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '09xxxxxxxx'}),
            'identity_card': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'current_apartment': forms.Select(attrs={'class': 'form-select select2'}),
            'relationship_type': forms.Select(attrs={'class': 'form-select'}),
            'identity_card_image_front': forms.FileInput(attrs={'class': 'form-control'}),
            'identity_card_image_back': forms.FileInput(attrs={'class': 'form-control'}),
        }

class VehicleForm(forms.ModelForm):
    """Form quản lý phương tiện"""
    class Meta:
        model = Vehicle
        fields = ['resident', 'vehicle_type', 'license_plate', 'manufacturer', 'model', 'color']
        widgets = {
            'resident': forms.Select(attrs={'class': 'form-select select2'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-select'}),
            'license_plate': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: 59A-123.45', 'style': 'text-transform: uppercase;'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: Honda, Toyota'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: SH 150i, Vios'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
        }