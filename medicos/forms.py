from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class MedicoCadastroFormulario(UserCreationForm):
    email = forms.EmailField()
    crm = forms.IntegerField()
    cns_medico = forms.IntegerField()

    class Meta:
        model = User
        fields = ['username', 'email', 'crm',
         'cns_medico', 'password1', 'password2'
         ]