from django import forms
from .models import Medico
from usuarios.models import Usuario
from usuarios.forms import CustomUserCreationForm
from django.db import transaction


from django import forms
from .models import Medico
from usuarios.models import Usuario
from usuarios.forms import CustomUserCreationForm
from django.db import transaction
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class MedicoCadastroFormulario(CustomUserCreationForm):
    nome = forms.CharField(max_length=200, label="Nome completo")
    crm = forms.CharField(max_length=10, label="CRM")
    cns = forms.CharField(max_length=15, label="Cartão Nacional de Saúde (CNS)")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(Submit("submit", "Cadastrar Médico", css_class="btn btn-primary"))

        # Remove password help texts
        if 'password1' in self.fields:
            self.fields['password1'].help_text = ''
        if 'password2' in self.fields:
            self.fields['password2'].help_text = ''

        # Apply form-control to all fields by default
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect, forms.ClearableFileInput)):
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'

    class Meta(CustomUserCreationForm.Meta):
        model = Usuario
        fields = ["nome", "crm", "cns", "email", "password1", "password2"]

    @transaction.atomic
    def save(self):
        usuario = super().save(commit=False)
        usuario.is_medico = True
        usuario.save()
        medico = Medico(
            cns_medico=self.cleaned_data["cns"],
            crm_medico=self.cleaned_data["crm"],
            nome_medico=self.cleaned_data["nome"],
        )
        medico.save()
        usuario.medicos.add(medico)

        # clinica_cns = self.cleaned_data['cns_clinica']
        # clinica = Clinica.objects.create(cns=clinica_cns)
        # clinica.medicos.add(medico)
        # clinica.save()

        return usuario
