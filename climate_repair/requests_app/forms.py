from django import forms
from .models import Request, Comment, PartOrder

class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['equipment_type', 'model', 'problem_description', 'customer_name', 'customer_phone', 'status', 'assigned_to']
        widgets = {
            'problem_description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['equipment_type'].empty_label = "Выберите тип"
        self.fields['status'].empty_label = None
        self.fields['assigned_to'].empty_label = "Не назначен"

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Введите комментарий...'}),
        }

class PartOrderForm(forms.ModelForm):
    class Meta:
        model = PartOrder
        fields = ['part_name', 'quantity', 'received']