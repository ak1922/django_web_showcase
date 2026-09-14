from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm


AppUser = get_user_model()


class UserRegistrationForm(UserCreationForm):
    """
    Handles user registration/creation
    """

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={'class': 'form-control'}
        ),
        help_text=_('User Email')
    )

    class Meta:
        model = AppUser
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        """
        Dynamically injects Bootstrap classes into ALL active fields,
        including built-in username and password inputs.
        """
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        """Check for existing email in custom user table"""

        email = self.cleaned_data.get('email')

        if AppUser.objects.filter(email=email).exists():
            raise forms.ValidationError(_('A User account with this email already exists!'))
        return email
