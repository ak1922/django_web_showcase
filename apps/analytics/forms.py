from django import forms
from .models import SubscriptionEvent


class QuickSubscriptionEventForm(forms.ModelForm):

    class Meta:
        model = SubscriptionEvent
        fields = ['event_type', 'mrr_impact']
        widgets = {
            'event_type': forms.Select(attrs={
                'class': 'form-select form-select-sm'
            }),
            'mrr_impact': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'step': '0.01',
                'placeholder': 'e.g., 49.00'
            }),
        }
