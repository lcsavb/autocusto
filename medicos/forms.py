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
    """Form for registering new medical accounts.

    This form extends Django's `CustomUserCreationForm` to handle the registration
    of new doctors. It includes fields specific to a doctor's profile (name, CRM, CNS)
    and custom validation rules for these fields, as well as for email and password
    confirmation. It uses `crispy_forms` for rendering.

    Critique:
    - The form explicitly defines `nome`, `crm`, `cns`, and `email2` as `forms.CharField`
      or `forms.EmailField`. While this is functional, for fields directly mapping to a
      model, using `Meta` class and `fields` attribute is generally more concise and
      less error-prone. Custom validation can still be done via `clean_field_name` methods.
    - The `__init__` method contains a lot of manual configuration for `crispy_forms`
      and error messages. Some of this could potentially be streamlined by using a
      custom `FormHelper` class or by defining default error messages in the model
      fields themselves.
    - The `clean_password2` and `clean_email2` methods are good for confirming inputs.
    - The `clean_email`, `clean_crm`, and `clean_cns` methods perform validation that
      could potentially be moved to model-level validation or custom validators for
      better reusability and separation of concerns.
    - The `save` method handles the creation of both `Usuario` and `Medico` objects
      within a single atomic transaction, which is good for data integrity. However,
      the commented-out `clinica` creation suggests incomplete or evolving logic.
    """
    # English: name
    nome = forms.CharField(
        max_length=200, 
        label="Nome completo",
        error_messages={
            'required': 'Nome completo é obrigatório.',
            'max_length': 'Nome deve ter no máximo 200 caracteres.'
        }
    )
    # English: crm
    crm = forms.CharField(
        max_length=10, 
        label="CRM",
        error_messages={
            'required': 'CRM é obrigatório.',
            'max_length': 'CRM deve ter no máximo 10 caracteres.'
        }
    )
    # English: cns
    cns = forms.CharField(
        max_length=15, 
        label="Cartão Nacional de Saúde (CNS)",
        error_messages={
            'required': 'CNS é obrigatório.',
            'max_length': 'CNS deve ter no máximo 15 caracteres.'
        }
    )
    # English: email2
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
        # English: helper
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.attrs = {'novalidate': True}
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
        # English: model
        model = Usuario
        # English: fields
        fields = ["nome", "crm", "cns", "email", "email2", "password1", "password2"]

    # English: clean_password2
    def clean_password2(self):
        """Validate that the two password entries match."""
        # English: password1
        password1 = self.cleaned_data.get("password1")
        # English: password2
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("As senhas não coincidem.")
        return password2

    # English: clean_email2
    def clean_email2(self):
        """Validate that the two email entries match."""
        # English: email1
        email1 = self.cleaned_data.get("email")
        # English: email2
        email2 = self.cleaned_data.get("email2")
        if email1 and email2 and email1 != email2:
            raise forms.ValidationError("Os emails não coincidem.")
        return email2

    # English: clean_email
    def clean_email(self):
        """Validate that the email is unique."""
        # English: email
        email = self.cleaned_data.get("email")
        if email and Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Este email já está em uso.")
        return email

    # English: clean_crm
    def clean_crm(self):
        """Validate CRM format."""
        # English: crm
        crm = self.cleaned_data.get("crm")
        if crm and not crm.isdigit():
            raise forms.ValidationError("CRM deve conter apenas números.")
        return crm

    # English: clean_cns
    def clean_cns(self):
        """Validate CNS format."""
        # English: cns
        cns = self.cleaned_data.get("cns")
        if cns and (not cns.isdigit() or len(cns) != 15):
            raise forms.ValidationError("CNS deve conter exatamente 15 números.")
        return cns

    # English: save
    @transaction.atomic
    def save(self):
        # English: user
        usuario = super().save(commit=False)
        usuario.is_medico = True
        usuario.save()
        # English: doctor
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
