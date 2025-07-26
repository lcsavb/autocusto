"""
Prescription Forms - Complex forms for prescription creation and editing

This module contains the main prescription forms with simplified validation logic:
- NovoProcesso: New prescription form with extracted medication validation
- RenovarProcesso: Renewal form extending NovoProcesso
"""

import logging
from django import forms
from django.db import transaction
from django.forms.models import model_to_dict
from processos.models import Processo, Doenca
from clinicas.models import Emissor
from .form_validators import MedicationValidator
from .base_forms import PrescriptionBaseMixin
from crispy_forms.helper import FormHelper

logger = logging.getLogger('processos')

# Constants for form choices
REPETIR_ESCOLHAS = [(True, "Sim"), (False, "Não")]


class NovoProcesso(PrescriptionBaseMixin, forms.Form):
    """
    New prescription form with simplified validation and extracted business logic.
    
    This form handles the creation of new medical prescriptions with dynamic
    medication fields and proper validation using the MedicationValidator class.
    """
    
    def __init__(self, escolhas, medicamentos, *args, **kwargs):
        super(NovoProcesso, self).__init__(*args, **kwargs)
        
        # Dynamically create medication fields to avoid repetition
        self._create_medication_fields()
        
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.attrs = {'novalidate': True}
        self.helper.form_show_errors = False  # Don't show inline error messages
        self.helper.error_text_inline = False  # Don't show error text but keep visual indicators
        self.helper.form_tag = False  # Don't wrap in form tags since we're using individual fields
        
        # Apply form-control to all fields by default and ensure proper error styling
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect, forms.ClearableFileInput)):
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'
            # Ensure field supports error styling
            field.widget.attrs['data-crispy-field'] = 'true'

        self.fields["clinicas"].choices = escolhas
        for i in range(1, 5):
            self.fields[f"id_med{i}"].choices = medicamentos
        self.request = kwargs.pop("request", None)
    
    def _create_medication_fields(self):
        """
        Dynamically generates medication-related form fields to eliminate code duplication.
        
        This method creates a comprehensive set of medication fields for up to 4 different medications,
        each with 6 months of dosage tracking. The dynamic approach prevents hundreds of lines of
        repetitive field definitions while maintaining flexibility for different medication scenarios.
        
        Field Structure per medication:
        - id_med{i}: Medication selection dropdown
        - med{i}_repetir_posologia: Whether to repeat the same dosage across months
        - med{i}_posologia_mes{month}: Dosage instructions for each month (1-6)
        - qtd_med{i}_mes{month}: Quantity needed for each month (1-6)
        
        Business Rules:
        - Only med1 fields are required (Brazilian regulations require at least one medication)
        - med2-4 are optional for combination therapies
        - 6-month tracking aligns with Brazilian prescription renewal cycles
        """
        # Generate fields for up to 4 different medications
        for i in range(1, 5):
            # Medication selection dropdown - populated later with available medications
            self.fields[f"id_med{i}"] = forms.ChoiceField(
                widget=forms.Select(attrs={"class": "custom-select"}),
                choices=[],  # Will be populated in __init__ with actual medication options
                label="Nome",
                error_messages={'required': 'Por favor, selecione um medicamento.'}
            )
            
            # Dosage repetition control - determines if same dosage applies to all months
            self.fields[f"med{i}_repetir_posologia"] = forms.ChoiceField(
                required=True,
                initial=True,  # Default to repeating dosage (most common case)
                choices=REPETIR_ESCOLHAS,
                label="Repetir posologia?",
                widget=forms.Select(attrs={"class": "custom-select"}),
                error_messages={'required': 'Por favor, selecione uma opção.'}
            )
            
            # Generate dosage and quantity fields for 6-month prescription cycle
            for month in range(1, 7):
                # Business rule: Only first medication (med1) is mandatory
                is_required = (i == 1)
                
                # Dosage instructions for each month
                self.fields[f"med{i}_posologia_mes{month}"] = forms.CharField(
                    required=is_required,
                    label="Posologia",
                    error_messages={'required': 'Por favor, insira a posologia.'}
                )
                
                # Quantity needed for each month
                self.fields[f"qtd_med{i}_mes{month}"] = forms.CharField(
                    required=is_required,
                    label=f"Qtde. {month} mês",
                    error_messages={'required': 'Por favor, insira a quantidade.'}
                )
        
        # Administration route field - only needed for the primary medication
        self.fields["med1_via"] = forms.CharField(
            required=True,
            label="Via administração",
            error_messages={'required': 'Por favor, insira a via de administração.'}
        )

    # Patient data fields
    cpf_paciente = forms.CharField(
        required=True,
        label="CPF do paciente",
        max_length=14,
        widget=forms.TextInput(attrs={"readonly": "readonly", "size": 14}),
        error_messages={'required': 'Por favor, insira o CPF do paciente.'}
    )
    clinicas = forms.ChoiceField(
        widget=forms.Select(attrs={"class": "custom-select"}),
        choices=[],
        label="Selecione a clínica",
        error_messages={'required': 'Por favor, selecione uma clínica.'}
    )
    nome_paciente = forms.CharField(
        required=True, 
        label="Nome do paciente",
        error_messages={'required': 'Por favor, insira o nome do paciente.'}
    )
    nome_mae = forms.CharField(
        required=True, 
        label="Nome da mãe",
        error_messages={'required': 'Por favor, insira o nome da mãe.'}
    )
    peso = forms.IntegerField(
        required=True, 
        label="Peso (kg)",
        error_messages={'required': 'Por favor, insira o peso.'}
    )
    altura = forms.IntegerField(
        required=True, 
        label="Altura (centímetros)",
        error_messages={'required': 'Por favor, insira a altura.'}
    )
    end_paciente = forms.CharField(
        required=True, 
        label="Endereço (com complemento)",
        error_messages={'required': 'Por favor, insira o endereço.'}
    )
    incapaz = forms.BooleanField(
        label="É incapaz?",
        initial=False,
        required=False,
        widget=forms.RadioSelect(
            choices=[(False, "Não"), (True, "Sim")],
            attrs={"class": "form-check-inline"}
        ),
    )
    nome_responsavel = forms.CharField(
        label="Nome do responsável",
        required=False,
        widget=forms.TextInput(attrs={"class": "cond-incapaz"}),
    )
    consentimento = forms.ChoiceField(
        initial=False,
        label="Protocolo 1ª vez: ",
        choices=[(False, "Não"), (True, "Sim")],
        widget=forms.RadioSelect(attrs={"class": "form-check-inline"}),
    )
    cid = forms.CharField(
        required=True,
        label="CID",
        widget=forms.TextInput(attrs={"readonly": "readonly", "size": 5}),
        error_messages={'required': 'Por favor, insira o CID.'}
    )
    diagnostico = forms.CharField(
        required=True,
        label="Diagnóstico",
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
        error_messages={'required': 'Por favor, insira o diagnóstico.'}
    )
    anamnese = forms.CharField(
        required=True, 
        label="Anamnese", 
        error_messages={'required': 'Por favor, insira a anamnese.'}
    )
    preenchido_por = forms.ChoiceField(
        initial="paciente",
        choices=[
            ("paciente", "Paciente"),
            ("mae", "Mãe"),
            ("responsavel", "Responsável"),
            ("medico", "Médico"),
        ],
        widget=forms.RadioSelect(attrs={"class": "form-check-inline"}),
    )
    etnia = forms.ChoiceField(
        label="Etnia",
        required=False,
        choices=[
            ("etnia_branca", "Branca"),
            ("etnia_parda", "Parda"),
            ("etnia_amarela", "Amarela"),
            ("etnia_indigena", "Indígena"),
            ("etnia_si", "Sem informação"),
        ],
        widget=forms.Select(attrs={"class": "custom-select cond-campo-18"}),
    )
    email_paciente = forms.EmailField(
        required=False,
        label="E-Mail",
        widget=forms.TextInput(attrs={"class": "cond-campo-18"}),
    )
    telefone1_paciente = forms.CharField(
        required=False,
        label="Tel. residencial",
        widget=forms.TextInput(attrs={"class": "cond-campo-18"}),
    )
    telefone2_paciente = forms.CharField(
        required=False,
        label="Celular",
        widget=forms.TextInput(attrs={"class": "cond-campo-18"}),
    )
    tratou = forms.ChoiceField(
        choices=((False, "Não"), (True, "Sim")),
        label="Fez tratamento prévio?",
        initial=False,
        widget=forms.RadioSelect(attrs={"class": "form-check-inline"}),
    )
    tratamentos_previos = forms.CharField(
        label="Descrição dos tratamentos prévios",
        required=False,
        widget=forms.TextInput(attrs={"class": "cond-trat"}),
    )
    data_1 = forms.DateField(
        required=True,
        label="Data",
        widget=forms.DateInput(format="%d/%m/%Y"),
        input_formats=["%d/%m/%Y"],
        error_messages={'required': 'Por favor, insira a data.'}
    )
    relatorio = forms.CharField(
        label="Relatório",
        required=False,
        widget=forms.Textarea(
            attrs={"class": "relatorio", "rows": "6", "width": "100%"}
        ),
    )
    emitir_relatorio = forms.ChoiceField(
        initial=False,
        label="Emissão de relatório: ",
        choices=[(False, "Não"), (True, "Sim")],
        widget=forms.RadioSelect(attrs={"class": "emitir-relatorio form-check-inline"}),
    )
    emitir_exames = forms.ChoiceField(
        initial=False,
        label="Emissão de exames: ",
        choices=[(False, "Não"), (True, "Sim")],
        widget=forms.RadioSelect(attrs={"class": "form-check-inline"}),
    )
    exames = forms.CharField(
        label="Exames",
        required=False,
        widget=forms.Textarea(attrs={"class": "exames", "rows": "6"}),
    )

    def clean(self):
        """
        Custom form validation with simplified control flow using MedicationValidator.
        
        This method replaces the original 150+ line nested validation logic with
        a clean, early-return pattern using the extracted MedicationValidator class.
        """
        cleaned_data = super().clean()
        
        # Use validator class for medication validation
        medication_validator = MedicationValidator(self.data)
        submitted_medications = medication_validator.get_submitted_medications()
        
        # Early return if no medications submitted
        if not submitted_medications:
            self.add_error(None, "Pelo menos um medicamento deve ser selecionado.")
            logger.info("VALIDATION ERROR: No medications submitted - form is invalid")
            return cleaned_data
        
        # Validate each submitted medication
        for med_num in submitted_medications:
            medication_validator.validate_medication(med_num, self)
        
        # Clean up validation errors for unused medications
        medication_validator.cleanup_unused_medication_errors(self, submitted_medications)
        
        logger.info(f"Form validation complete - {len(submitted_medications)} medications validated")
        return cleaned_data

    @transaction.atomic
    def save(self, usuario, medico, meds_ids):
        """
        Saves a new prescription process following proper Django patterns.
        
        This method uses PrescriptionDataService for data construction and
        PrescriptionDatabaseService for database operations, maintaining
        clean separation of concerns.
        """
        from ..repositories.patient_repository import PatientRepository
        from ..repositories.domain_repository import DomainRepository
        from ..services.prescription.data_builder import PrescriptionDataBuilder
        from ..services.prescription.process_repository import ProcessRepository
        
        dados = self.cleaned_data
        clinica_id = dados["clinicas"]
        cid = dados["cid"]
        cpf_paciente = dados["cpf_paciente"]
        
        # Use repositories instead of direct database operations
        domain_repo = DomainRepository()
        doenca = domain_repo.get_disease_by_cid(cid)
        emissor = domain_repo.get_emissor_by_medico_clinica(medico, medico.clinicas.get(id=clinica_id))

        # Check if patient exists
        patient_repo = PatientRepository()
        paciente_existe = patient_repo.check_patient_exists(cpf_paciente)

        # Step 1: Use DataBuilder for data construction
        data_service = PrescriptionDataBuilder()
        structured_data = data_service.build_prescription_data(
            dados, meds_ids, doenca, emissor, usuario, 
            paciente_existe=paciente_existe, cid=cid
        )

        # Step 2: Use ProcessRepository with structured data
        db_service = ProcessRepository()
        processo_id = db_service.create_process_from_structured_data(structured_data)

        return processo_id


class RenovarProcesso(NovoProcesso):
    """
    Renewal form extending NovoProcesso with additional renewal-specific fields.
    
    This form adds the ability to choose between complete renewal (all fields)
    or quick renewal (date change only).
    """
    edicao_completa = forms.ChoiceField(
        required=True,
        initial=False,
        choices=[(False, "Não"), (True, "Sim")],
        widget=forms.RadioSelect(attrs={"class": "form-check-inline"}),
        error_messages={'required': 'Por favor, selecione uma opção.'}
    )

    @transaction.atomic
    def save(self, usuario, medico, processo_id, meds_ids):
        """
        Save renewal process with simplified control flow.
        
        Uses early returns to handle the two renewal modes clearly:
        1. Complete renewal - full form processing
        2. Quick renewal - date update only
        """
        from ..repositories.patient_repository import PatientRepository
        from ..services.prescription.process_repository import ProcessRepository
        
        dados = self.cleaned_data
        edicao_completa = dados["edicao_completa"]

        if edicao_completa == "True":
            # Complete renewal - process all form data
            self._handle_complete_renewal(dados, meds_ids, medico, usuario, processo_id)
            return processo_id
        else:
            # Quick renewal - update date only
            self._handle_quick_renewal(dados, meds_ids, processo_id)
            return processo_id

    def _handle_complete_renewal(self, dados, meds_ids, medico, usuario, processo_id):
        """Handle complete renewal with full form processing."""
        from ..repositories.patient_repository import PatientRepository
        from ..services.prescription.process_repository import ProcessRepository
        
        cpf_paciente = dados["cpf_paciente"]
        patient_repo = PatientRepository()
        paciente_existe = patient_repo.check_patient_exists(cpf_paciente)
        clinica_id = dados["clinicas"]
        
        # Use repositories instead of direct database operations
        from ..repositories.domain_repository import DomainRepository
        domain_repo = DomainRepository()
        doenca = domain_repo.get_disease_by_cid(dados["cid"])
        emissor = domain_repo.get_emissor_by_medico_clinica(medico, medico.clinicas.get(id=clinica_id))

        # Use DataBuilder for structured data construction
        from ..services.prescription.data_builder import PrescriptionDataBuilder
        data_service = PrescriptionDataBuilder()
        structured_data = data_service.build_prescription_data(
            dados, meds_ids, doenca, emissor, usuario, 
            paciente_existe=paciente_existe, cid=dados["cid"], processo_id=processo_id
        )
        
        # Use ProcessRepository with structured data for updates
        registration_service = ProcessRepository()
        registration_service.update_process_from_structured_data(processo_id, structured_data)

    def _handle_quick_renewal(self, dados, meds_ids, processo_id):
        """Handle quick renewal with date update only."""
        from ..services.prescription.process_repository import ProcessRepository
        
        # Partial renewal - update only the date  
        # Use ProcessRepository for quick date update instead of direct database operations
        registration_service = ProcessRepository()
        registration_service.update_process_date_only(processo_id, dados['data_1'], meds_ids)