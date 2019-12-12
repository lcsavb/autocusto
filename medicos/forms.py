from django import forms
from .models import Medico
from django.contrib.auth.forms import UserCreationForm

class MedicoCadastroFormulario(UserCreationForm):
    
    class Meta:
        model = Medico
        fields = ['email', 'nome', 'crm', 'cns', 'password1', 'password2']