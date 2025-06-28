from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class SetPasswordForOAuthUserForm(SetPasswordForm):
    """
    Custom form for setting a password for OAuth users who don't have one.
    This form allows Google-authenticated users to set a password for email/password login.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize field labels and help text
        self.fields['new_password1'].label = 'New Password'
        self.fields['new_password1'].help_text = (
            'Create a password to enable email/password login alongside your Google account. '
            'Your password must be at least 8 characters long and cannot be too similar to your other personal information.'
        )
        self.fields['new_password2'].label = 'Confirm New Password'
        self.fields['new_password2'].help_text = 'Enter the same password as before, for verification.'
        
        # Add CSS classes for styling
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control bg-secondary text-white border-secondary',
                'placeholder': field.label
            })

    def clean_new_password1(self):
        password1 = self.cleaned_data.get('new_password1')
        if password1:
            validate_password(password1, self.user)
        return password1


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile information."""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add CSS classes for styling
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control bg-secondary text-white border-secondary'
            })
        
        # Customize field labels
        self.fields['first_name'].label = 'First Name'
        self.fields['last_name'].label = 'Last Name'
        self.fields['email'].label = 'Email Address'
        self.fields['email'].help_text = 'This email will be used for password reset and notifications.'


class RemovePasswordForm(forms.Form):
    """Form for removing password from OAuth users who want to use only OAuth."""
    
    confirm = forms.BooleanField(
        required=True,
        label='I understand that removing my password will disable email/password login',
        help_text='You will only be able to log in using your Google account after removing your password.',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )