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
    nome = forms.CharField(
        max_length=200, 
        label="Nome completo",
        error_messages={
            'required': 'Nome completo é obrigatório.',
            'max_length': 'Nome deve ter no máximo 200 caracteres.'
        }
    )
    crm = forms.CharField(
        max_length=10, 
        label="CRM",
        error_messages={
            'required': 'CRM é obrigatório.',
            'max_length': 'CRM deve ter no máximo 10 caracteres.'
        }
    )
    cns = forms.CharField(
        max_length=15, 
        label="Cartão Nacional de Saúde (CNS)",
        error_messages={
            'required': 'CNS é obrigatório.',
            'max_length': 'CNS deve ter no máximo 15 caracteres.'
        }
    )
    email2 = forms.EmailField(
        label="Confirmar email",
        error_messages={
            'required': 'Confirmação de email é obrigatória.',
            'invalid': 'Digite um email válido.'
        }
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configure Crispy Forms helper
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        # Don't add submit button here - using custom button in template
        
        # Configure crispy to NOT show inline errors (we'll show them as toasts)
        self.helper.form_show_errors = False
        self.helper.error_text_inline = False
        self.helper.help_text_inline = True

        # Customize error messages for password fields
        if 'password1' in self.fields:
            self.fields['password1'].help_text = ''
            self.fields['password1'].error_messages = {
                'required': 'Por favor, insira uma senha.'
            }
            
        if 'password2' in self.fields:
            self.fields['password2'].help_text = ''
            self.fields['password2'].error_messages = {
                'required': 'Por favor, confirme a senha.'
            }

        # Customize email field
        if 'email' in self.fields:
            self.fields['email'].error_messages = {
                'required': 'Email é obrigatório.',
                'invalid': 'Digite um email válido.',
                'unique': 'Este email já está em uso.'
            }

        # Apply form-control to all fields by default
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect, forms.ClearableFileInput)):
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'

    class Meta(CustomUserCreationForm.Meta):
        model = Usuario
        fields = ["nome", "crm", "cns", "email", "email2", "password1", "password2"]

    def clean_password2(self):
        """Validate that the two password entries match."""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("As senhas não coincidem.")
        return password2

    def clean_email2(self):
        """Validate that the two email entries match."""
        email1 = self.cleaned_data.get("email")
        email2 = self.cleaned_data.get("email2")
        if email1 and email2 and email1 != email2:
            raise forms.ValidationError("Os emails não coincidem.")
        return email2

    def clean_email(self):
        """Validate that the email is unique."""
        email = self.cleaned_data.get("email")
        if email and Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Este email já está em uso.")
        return email

    def clean_crm(self):
        """Validate CRM format."""
        crm = self.cleaned_data.get("crm")
        if crm and not crm.isdigit():
            raise forms.ValidationError("CRM deve conter apenas números.")
        return crm

    def clean_cns(self):
        """Validate CNS format."""
        cns = self.cleaned_data.get("cns")
        if cns and (not cns.isdigit() or len(cns) != 15):
            raise forms.ValidationError("CNS deve conter exatamente 15 números.")
        return cns

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
