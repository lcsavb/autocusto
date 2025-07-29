from django import forms
from .models import Medico, BRAZILIAN_STATES, MEDICAL_SPECIALTIES
from usuarios.models import Usuario
from usuarios.forms import CustomUserCreationForm
from django.db import transaction
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column

# Import services
from .services.doctor_registration_service import DoctorRegistrationService
from .services.doctor_profile_service import DoctorProfileService


# doctor registration form
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
        fields = ["nome", "email", "email2", "password1", "password2"]

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
        """Validate that the two email entries match (case-insensitive)."""
        # English: email1
        email1 = self.cleaned_data.get("email")
        # English: email2
        email2 = self.cleaned_data.get("email2")
        if email1 and email2:
            email2 = email2.lower()  # Normalize to lowercase
            if email1.lower() != email2:
                raise forms.ValidationError("Os emails não coincidem.")
        return email2

    # English: clean_email
    def clean_email(self):
        """Validate that the email is unique and normalize to lowercase."""
        # English: email
        email = self.cleaned_data.get("email")
        if email:
            email = email.lower()  # Normalize to lowercase for case-insensitive comparison
            from medicos.repositories.doctor_repository import DoctorRepository
            doctor_repo = DoctorRepository()
            if doctor_repo.check_email_exists(email):
                raise forms.ValidationError("Este email já está em uso.")
        return email



    def save(self):
        """Save new doctor registration using DoctorRegistrationService."""
        registration_service = DoctorRegistrationService()
        
        # Prepare registration data
        registration_data = {
            'email': self.cleaned_data['email'],
            'password1': self.cleaned_data['password1'],
            'password2': self.cleaned_data['password2'],
            'nome': self.cleaned_data['nome']
        }
        
        # Register new doctor
        usuario, medico = registration_service.register_new_doctor(registration_data)
        return usuario


class ProfileCompletionForm(forms.Form):
    """Form for completing CRM, CNS, specialty and state data."""
    
    crm = forms.CharField(
        max_length=10, 
        label="CRM",
        error_messages={
            'required': 'CRM é obrigatório.',
            'max_length': 'CRM deve ter no máximo 10 caracteres.'
        }
    )
    crm2 = forms.CharField(
        max_length=10, 
        label="Confirmar CRM",
        error_messages={
            'required': 'Confirmação de CRM é obrigatória.',
            'max_length': 'CRM deve ter no máximo 10 caracteres.'
        }
    )
    estado = forms.ChoiceField(
        choices=BRAZILIAN_STATES,
        label="Estado do CRM",
        error_messages={
            'required': 'Estado do CRM é obrigatório.',
            'invalid_choice': 'Selecione um estado válido.'
        }
    )
    especialidade = forms.ChoiceField(
        choices=MEDICAL_SPECIALTIES,
        label="Especialidade Médica",
        error_messages={
            'required': 'Especialidade médica é obrigatória.',
            'invalid_choice': 'Selecione uma especialidade válida.'
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
    cns2 = forms.CharField(
        max_length=15, 
        label="Confirmar CNS",
        error_messages={
            'required': 'Confirmação de CNS é obrigatória.',
            'max_length': 'CNS deve ter no máximo 15 caracteres.'
        }
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Check if CRM/CNS are already set (immutable once set)
        if self.user:
            medico = self.user.medicos.first()
            if medico:
                if medico.crm_medico:
                    self.initial['crm'] = medico.crm_medico
                    self.fields['crm'].disabled = True
                    self.fields['crm2'].disabled = True
                    self.fields['crm2'].required = False
                    self.fields['crm'].help_text = "CRM já definido e não pode ser alterado"
                if medico.cns_medico:
                    self.initial['cns'] = medico.cns_medico
                    self.fields['cns'].disabled = True
                    self.fields['cns2'].disabled = True
                    self.fields['cns2'].required = False
                    self.fields['cns'].help_text = "CNS já definido e não pode ser alterado"
                if medico.estado:
                    self.initial['estado'] = medico.estado
                    if medico.crm_medico:  # Only disable if CRM is also set
                        self.fields['estado'].disabled = True
                        self.fields['estado'].help_text = "Estado do CRM já definido e não pode ser alterado"
                if medico.especialidade:
                    self.initial['especialidade'] = medico.especialidade
        
        # Configure Crispy Forms helper
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.attrs = {'novalidate': True}
        self.helper.form_show_errors = False
        self.helper.error_text_inline = False
        self.helper.help_text_inline = True
        self.helper.layout = Layout(
            Row(
                Column('crm', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('estado', css_class='form-group col-md-6 mb-0'),
                Column('especialidade', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('cns', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
        )
        self.helper.add_input(Submit("submit", "Continuar para Clínicas", css_class="btn btn-primary float-right mt-3"))

        # Apply form-control to all fields except certain widgets
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect, forms.ClearableFileInput)):
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'

    def clean_crm(self):
        """Validate CRM format and uniqueness with state."""
        crm = self.cleaned_data.get("crm")
        if crm and not crm.isdigit():
            raise forms.ValidationError("CRM deve conter apenas números.")
        return crm
    
    def clean(self):
        """Validate CRM+State uniqueness together and business rules."""
        cleaned_data = super().clean()
        crm = cleaned_data.get("crm")
        estado = cleaned_data.get("estado")
        cns = cleaned_data.get("cns")
        
        if self.user:
            current_medico = self.user.medicos.first()
            
            # Business rule: CRM cannot be changed once set
            if current_medico and current_medico.crm_medico and crm and current_medico.crm_medico != crm:
                self.add_error('crm', "CRM não pode ser alterado após cadastro inicial")
            
            # Business rule: CNS cannot be changed once set
            if current_medico and current_medico.cns_medico and cns and current_medico.cns_medico != cns:
                self.add_error('cns', "CNS não pode ser alterado após cadastro inicial")
            
            # Check if CRM+State combination already exists for another medico
            if crm and estado:
                from medicos.repositories.doctor_repository import DoctorRepository
                doctor_repo = DoctorRepository()
                # Use raw QuerySet access through repository for complex filtering
                existing_medico = doctor_repo.check_crm_conflict(crm, estado, current_medico.id if current_medico else None)
                if existing_medico:
                    self.add_error('crm', f"Este CRM já está sendo usado por outro médico no estado {dict(BRAZILIAN_STATES)[estado]}.")
        
        return cleaned_data

    def clean_cns(self):
        """Validate CNS format and uniqueness."""
        cns = self.cleaned_data.get("cns")
        if cns and (not cns.isdigit() or len(cns) != 15):
            raise forms.ValidationError("CNS deve conter exatamente 15 números.")
        
        # Check if CNS already exists for another medico
        if cns and self.user:
            current_medico = self.user.medicos.first()
            from medicos.repositories.doctor_repository import DoctorRepository
            doctor_repo = DoctorRepository()
            existing_medico = doctor_repo.check_cns_conflict(cns, current_medico.id if current_medico else None)
            if existing_medico:
                raise forms.ValidationError("Este CNS já está sendo usado por outro médico.")
        
        return cns

    def clean_crm2(self):
        """Validate that the two CRM entries match."""
        crm1 = self.cleaned_data.get("crm")
        crm2 = self.cleaned_data.get("crm2")
        if crm1 and crm2 and crm1 != crm2:
            raise forms.ValidationError("Os CRMs não coincidem.")
        return crm2

    def clean_cns2(self):
        """Validate that the two CNS entries match."""
        cns1 = self.cleaned_data.get("cns")
        cns2 = self.cleaned_data.get("cns2")
        if cns1 and cns2 and cns1 != cns2:
            raise forms.ValidationError("Os CNSs não coincidem.")
        return cns2


    def save(self):
        """Complete doctor profile using DoctorProfileService."""
        if not self.user:
            raise ValueError("User is required")
        
        profile_service = DoctorProfileService()
        
        # Prepare profile completion data
        profile_data = {
            'crm': self.cleaned_data['crm'],
            'cns': self.cleaned_data['cns'],
            'estado': self.cleaned_data['estado'],
            'especialidade': self.cleaned_data['especialidade']
        }
        
        # Complete profile
        medico = profile_service.complete_doctor_profile(self.user, profile_data)
        return self.user


class UserDoctorEditForm(forms.Form):
    """Form for editing User and Doctor information."""
    
    # User fields
    name = forms.CharField(
        max_length=200, 
        label="Nome completo",
        required=False,
        error_messages={
            'max_length': 'Nome deve ter no máximo 200 caracteres.'
        }
    )
    email = forms.EmailField(
        label="Email",
        disabled=True,
        required=False,
        error_messages={
            'invalid': 'Digite um email válido.'
        }
    )
    
    # Doctor fields
    crm = forms.CharField(
        max_length=10, 
        label="CRM",
        required=False,
        error_messages={
            'max_length': 'CRM deve ter no máximo 10 caracteres.'
        }
    )
    estado = forms.ChoiceField(
        choices=BRAZILIAN_STATES,
        label="Estado do CRM",
        required=False,
        error_messages={
            'invalid_choice': 'Selecione um estado válido.'
        }
    )
    especialidade = forms.ChoiceField(
        choices=MEDICAL_SPECIALTIES,
        label="Especialidade Médica",
        required=False,
        error_messages={
            'invalid_choice': 'Selecione uma especialidade válida.'
        }
    )
    cns = forms.CharField(
        max_length=15, 
        label="Cartão Nacional de Saúde (CNS)",
        required=False,
        error_messages={
            'max_length': 'CNS deve ter no máximo 15 caracteres.'
        }
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Check if CRM/CNS are already set (immutable once set)
        if self.user:
            medico = self.user.medicos.first()
            if medico:
                self.initial['name'] = medico.nome_medico
                self.initial['email'] = self.user.email
                if medico.crm_medico:
                    self.initial['crm'] = medico.crm_medico
                    self.fields['crm'].disabled = True
                    self.fields['crm'].help_text = "CRM já definido e não pode ser alterado"
                if medico.cns_medico:
                    self.initial['cns'] = medico.cns_medico
                    self.fields['cns'].disabled = True
                    self.fields['cns'].help_text = "CNS já definido e não pode ser alterado"
                if medico.estado:
                    self.initial['estado'] = medico.estado
                    if medico.crm_medico:  # Only disable if CRM is also set
                        self.fields['estado'].disabled = True
                        self.fields['estado'].help_text = "Estado do CRM já definido e não pode ser alterado"
                if medico.especialidade:
                    self.initial['especialidade'] = medico.especialidade
        
        # Configure Crispy Forms helper
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.form_action = ""
        self.helper.attrs = {'novalidate': True}
        self.helper.form_show_errors = False
        self.helper.error_text_inline = False
        self.helper.help_text_inline = True
        self.helper.add_input(Submit("submit", "Atualizar Perfil", css_class="btn btn-primary float-right mt-3"))
        
        # Add spacing between form fields
        from crispy_forms.layout import Layout, Div
        self.helper.layout = Layout(
            Div('name', css_class="mb-4"),
            Div('email', css_class="mb-4"), 
            Div('crm', css_class="mb-4"),
            Div('estado', css_class="mb-4"),
            Div('especialidade', css_class="mb-4"),
            Div('cns', css_class="mb-4"),
        )

        # Apply form-control to all fields
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect, forms.ClearableFileInput)):
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'

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

    def save(self):
        """Update User and Doctor information using DoctorProfileService."""
        if not self.user:
            raise ValueError("User is required for editing")
        
        profile_service = DoctorProfileService()
        
        # Prepare update data (only include fields that have values)
        update_data = {}
        if self.cleaned_data.get("name"):
            update_data['nome'] = self.cleaned_data["name"]
        if self.cleaned_data.get("crm"):
            update_data['crm'] = self.cleaned_data["crm"]
        if self.cleaned_data.get("cns"):
            update_data['cns'] = self.cleaned_data["cns"]
        if self.cleaned_data.get("estado"):
            update_data['estado'] = self.cleaned_data["estado"]
        if self.cleaned_data.get("especialidade"):
            update_data['especialidade'] = self.cleaned_data["especialidade"]
        
        # Check if user has doctor profile, create if needed
        if not profile_service.doctor_repository.get_doctor_by_user(self.user):
            # Create new doctor profile
            registration_service = DoctorRegistrationService()
            doctor_data = registration_service.doctor_repository.extract_doctor_data(update_data)
            registration_service.doctor_repository.create_doctor(self.user, doctor_data)
        else:
            # Update existing profile
            profile_service.update_doctor_profile(self.user, update_data)
        
        return self.user
