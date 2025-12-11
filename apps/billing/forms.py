from django import forms
from .models import Invoice
from apps.buildings.models import Apartment
import datetime

class InvoiceForm(forms.ModelForm):
    """Form tạo hóa đơn thủ công"""
    apartment = forms.ModelChoiceField(
        queryset=Apartment.objects.all().order_by('floor_number', 'unit_number'),
        label="Căn hộ",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Invoice
        # Đã XÓA 'title' khỏi danh sách fields
        fields = ['apartment', 'month', 'year', 'total_amount', 'status', 'due_date', 'note']
        widgets = {
            'month': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'VNĐ'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = datetime.date.today()
        self.fields['month'].initial = today.month
        self.fields['year'].initial = today.year