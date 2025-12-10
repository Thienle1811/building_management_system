from django import forms
from django.contrib.auth.models import User
from .models import StaffProfile, ShiftConfig

class StaffProfileForm(forms.ModelForm):
    """Form cập nhật thông tin nhân viên (Sửa)"""
    # Thêm các trường từ User model để sửa tiện hơn
    first_name = forms.CharField(label="Họ", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label="Tên", required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Email", required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = StaffProfile
        fields = ['phone', 'team', 'status', 'avatar']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'team': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Nếu đang sửa (có instance), điền dữ liệu User vào form
        if self.instance and self.instance.pk:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        # Lưu StaffProfile
        staff = super().save(commit=False)
        # Lưu thông tin User đi kèm
        if staff.user:
            staff.user.first_name = self.cleaned_data['first_name']
            staff.user.last_name = self.cleaned_data['last_name']
            staff.user.email = self.cleaned_data['email']
            if commit:
                staff.user.save()
                staff.save()
        return staff

class StaffCreationForm(StaffProfileForm):
    """Form tạo nhân viên mới (kèm tạo User)"""
    username = forms.CharField(label="Tên đăng nhập", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Mật khẩu", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def save(self, commit=True):
        # Tạo User trước
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data['email']
        )
        # Tạo StaffProfile liên kết với User
        staff = super(StaffProfileForm, self).save(commit=False)
        staff.user = user
        if commit:
            staff.save()
        return staff

class ShiftConfigForm(forms.ModelForm):
    """Form cấu hình Ca trực"""
    class Meta:
        model = ShiftConfig
        fields = ['name', 'start_time', 'end_time', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }