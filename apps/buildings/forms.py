from django import forms
from .models import Building

class ApartmentImportForm(forms.Form):
    building = forms.ModelChoiceField(
        queryset=Building.objects.all(),
        label="Chọn Tòa nhà",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    excel_file = forms.FileField(
        label="File Excel danh sách căn hộ (.xlsx)",
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx'})
    )