from django import forms
from .models import FeedbackCategory

class FeedbackCategoryForm(forms.ModelForm):
    class Meta:
        model = FeedbackCategory
        fields = ['name', 'code', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Thêm class form-control cho giao diện đẹp
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        
        # Mã code nên viết hoa
        self.fields['code'].widget.attrs['style'] = 'text-transform: uppercase;'