from django import forms
from .models import Paciente

class PacienteCadastroFormulario(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['nome_paciente', 'nome_mae', 'cpf_paciente']