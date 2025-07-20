from django.contrib.auth.forms import UserCreationForm, UserChangeForm

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
