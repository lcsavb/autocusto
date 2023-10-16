
from django import forms
from .models import Paciente

class PacienteCadastroFormulario(forms.ModelForm):

    class Meta():
        model = Paciente
        fields = ['patient_name', 'mother_name', 'patient_cpf']
