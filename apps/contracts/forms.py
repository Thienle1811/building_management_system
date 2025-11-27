from django import forms
from django.core.exceptions import ValidationError # <--- Nhớ import thêm cái này
from .models import Contract

class ContractForm(forms.ModelForm):
    # ... (giữ nguyên phần class Meta và __init__ cũ) ...

    class Meta:
        model = Contract
        fields = [
            'code', 'apartment', 'resident', 
            'contract_type', 'status', 
            'start_date', 'end_date', 
            'deposit_amount', 'contract_file', 'note'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'note': forms.Textarea(attrs={'rows': 3}),
            'deposit_amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super(ContractForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.widget.__class__.__name__ == 'Select':
                field.widget.attrs['class'] = 'form-select'
            elif field.widget.__class__.__name__ not in ['DateInput', 'Textarea', 'NumberInput', 'FileInput']:
                field.widget.attrs['class'] = 'form-control'

    # --- PHẦN MỚI THÊM VÀO ---
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # 1. Kiểm tra ngày kết thúc phải sau ngày bắt đầu
        if start_date and end_date:
            if end_date < start_date:
                # Báo lỗi hiển thị ngay tại trường end_date
                self.add_error('end_date', "Ngày kết thúc không được nhỏ hơn ngày bắt đầu.")

        # 2. (Nâng cao) Kiểm tra trùng lặp hợp đồng (nếu cần thiết sau này)
        # apartment = cleaned_data.get('apartment')
        # if apartment and start_date:
        #     ... logic check trùng ...
        
        return cleaned_data