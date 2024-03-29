from django import forms
from django.forms import ModelForm
from .models import Medico
from clinicas.models import Clinica
from usuarios.models import Usuario
from usuarios.forms import CustomUserCreationForm
from django.db import transaction

class MedicoCadastroFormulario(CustomUserCreationForm):
    nome = forms.CharField(max_length=200, label='Nome completo')
    crm = forms.CharField(max_length=10, label='CRM')
    cns = forms.CharField(max_length=15, label='Cartão Nacional de Saúde (CNS)')

    class Meta(CustomUserCreationForm.Meta):
        model = Usuario
        fields = ['nome', 'crm', 'cns',
         'email', 'password1', 'password2']

    @transaction.atomic
    def save(self):
        usuario = super().save(commit=False)
        usuario.is_medico = True
        usuario.save()
        medico = Medico(cns_medico=self.cleaned_data['cns'],
                        crm_medico=self.cleaned_data['crm'],
                        nome_medico=self.cleaned_data['nome'])
        medico.save()
        usuario.medicos.add(medico)


        # clinica_cns = self.cleaned_data['cns_clinica']
        # clinica = Clinica.objects.create(cns=clinica_cns)
        # clinica.medicos.add(medico)
        # clinica.save()

        return usuario