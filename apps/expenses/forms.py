from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from .models import ExpenseReport


AppUser = get_user_model()


class ExpenseReportForm(forms.ModelForm):
    class Meta:
        model = ExpenseReport
        fields = [
            'title',
            'amount',
            'description',
            'assigned_manager'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('e.g., Q3 Travel Expenses')
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Provide business justification...')
            }),
            'assigned_manager': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['assigned_manager'].queryset = AppUser.objects.filter(
            expense_profile__role__in=['MANAGER', 'FINANCE_ADMIN']
        ).distinct()
