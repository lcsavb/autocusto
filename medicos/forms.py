from django import forms
from .models import Medico
from clinicas.models import Clinica
from usuarios.models import Usuario
from usuarios.forms import CustomUserCreationForm
from django.db import transaction

class MedicoCadastroFormulario(CustomUserCreationForm):
    nome = forms.CharField(max_length=200, label='Nome completo')
    crm = forms.CharField(max_length=10, label='CRM')
    cns = forms.CharField(max_length=15, label='Cartão Nacional de Saúde (CNS)')
    cns_clinica = forms.CharField(max_length=15, label='CNS da clínica') 

    class Meta(CustomUserCreationForm.Meta):
        model = Usuario
        fields = ['nome', 'crm', 'cns', 'cns_clinica',
         'email', 'password1', 'password2']

    @transaction.atomic
    def save(self):
        print('entrou na função salvar')
        print(self.cleaned_data)
        usuario = super().save(commit=False)
        usuario.is_medico = True
        usuario.save()
        medico = Medico.objects.create(usuario=usuario)
        medico.cns_medico = self.cleaned_data['cns']
        medico.crm_medico = self.cleaned_data['crm']
        medico.nome_medico = self.cleaned_data['nome']
        medico.save(update_fields=['cns_medico', 'crm_medico', 'nome_medico'])

        # clinica_cns = self.cleaned_data['cns_clinica']
        # clinica = Clinica.objects.create(cns=clinica_cns)
        # clinica.medicos.add(medico)
        # clinica.save()

        return usuario