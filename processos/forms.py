from django import forms
from pacientes.models import Paciente
from medicos.models import Medico
from processos.models import Processo
from clinicas.models import Clinica

class NovoProcesso(forms.Form):
    cpf_paciente = forms.CharField(required=True)
    nome_paciente = forms.CharField(required=True)
    peso = forms.IntegerField(required=True)
    altura = forms.IntegerField(required=True)
    nome_mae = forms.CharField(required=True)
    cid = forms.CharField(required=True)
    diagnostico = forms.CharField(required=True)
    anamnese = forms.CharField(required=True)
    trat_previo = forms.BooleanField(required=True)
    tratamento_previo = forms.CharField()
    incapaz = forms.BooleanField(required=True)
    data1 = forms.DateField(required=True)

    def save(self):
        pass
