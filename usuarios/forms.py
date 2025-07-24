from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm, SetPasswordForm
from django import forms

from .models import Usuario


class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            del self.fields['username']

        self.fields["password1"].label = "Senha"
        self.fields["password2"].label = "Confirmar senha"
        self.fields["email"].label = "Endereço de email"

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ("email",)


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = Usuario
        fields = ("email",)


class CustomPasswordResetForm(PasswordResetForm):
    """Custom password reset form with Portuguese labels"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = "Endereço de email"
        self.fields['email'].help_text = "Digite o email associado à sua conta"


class CustomSetPasswordForm(SetPasswordForm):
    """Custom set password form with Portuguese labels and help text"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].label = "Nova senha"
        self.fields['new_password1'].help_text = None
        self.fields['new_password2'].label = "Confirmar nova senha"
        self.fields['new_password2'].help_text = "Digite a mesma senha novamente para confirmação"
        
        # Override error messages
        self.fields['new_password1'].error_messages = {
            'required': 'Este campo é obrigatório.',
        }
        self.fields['new_password2'].error_messages = {
            'required': 'Este campo é obrigatório.',
        }
    
    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("As duas senhas não coincidem.")
        return password2
