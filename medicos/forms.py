from django import forms
from .models import Medico
from usuarios.models import Usuario
from usuarios.forms import CustomUserCreationForm
from django.db import transaction

class MedicoCadastroFormulario(CustomUserCreationForm):
    crm = forms.CharField(max_length=10)
    cns = forms.CharField(max_length=15)

    class Meta(CustomUserCreationForm.Meta):
        model = Usuario

    @transaction.atomic
    def save(self):
        usuario = super().save(commit=False)
        usuario.is_medico = True
        usuario.save()
        medico = Medico.objects.create(usuario=usuario)
        medico.cns.add(*self.cleaned_data.get('cns'))
        medico.crm.add(*self.cleaned_data.get('crm'))
        return usuario