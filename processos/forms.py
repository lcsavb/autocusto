import logging
from django import forms
from django.db import transaction
from processos.models import Processo, Protocolo, Doenca
from clinicas.models import Emissor
from autocusto.validation import isCpfValid
from .repositories.patient_repository import PatientRepository
from .services.registration_service import ProcessRegistrationService
# Legacy import no longer needed - migrated protocols use data-driven approach
# from .seletor import seletor_campos
from .services.pdf_strategies import get_conditional_fields

logger = logging.getLogger('processos')

# show medication
def mostrar_med(mostrar, *args):
    """
    Dynamically controls medication tab visibility in the UI based on existing process data.
    
    This function determines which medication tabs should be visible in the form interface.
    By default, all medication tabs except the first one are hidden (using Bootstrap's 'd-none' class).
    When editing an existing process, this function reveals tabs for medications that are already
    associated with the process, ensuring users can see and edit existing medication data.
    
    Args:
        # English: show
        mostrar (bool): Whether to show medications (True for editing existing process, False for new)
        *args: Variable arguments, where args[0] should be a Processo instance when mostrar=True
    
    Returns:
        dict: CSS class mapping for medication tabs ('d-none' to hide, '' to show)
    """
    # Initialize all medication tabs as hidden except med1 (which is always shown)
    # English: dic
    dic = {
        "med2_mostrar": "d-none",
        "med3_mostrar": "d-none", 
        "med4_mostrar": "d-none",
    }
    
    if mostrar:
        # English: process
        processo = args[0]
        n = 1
        # Iterate through existing medications and reveal corresponding tabs
        # This ensures users can see all medications already associated with the process
        for med in processo.medicamentos.all():
            # English: dic
            dic[f"med{n}_mostrar"] = ""  # Remove 'd-none' class to show the tab
            n = n + 1
    return dic

# adjust conditional fields
def ajustar_campos_condicionais(dados_paciente):
    """
    Conditionally shows/hides form fields based on patient data and form completion context.
    
    This function implements complex business logic for Brazilian medical form regulations:
    1. If patient has email, it means the form is being filled digitally by a doctor (not patient)
    2. If patient is incapable (incapaz), a responsible person's name field must be shown
    3. Campo 18 refers to specific SUS (Brazilian health system) form fields that are only
       required when the form is filled by medical personnel rather than the patient
    
    Args:
        dados_paciente (dict): Patient data dictionary containing form field values
    
    Returns:
        tuple: (visibility_dict, modified_patient_data)
            - visibility_dict: CSS classes to show/hide conditional fields
            - modified_patient_data: Updated patient data with 'preenchido_por' field set
    """
    # Initialize all conditional fields as hidden by default
    dic = {"responsavel_mostrar": "d-none", "campo_18_mostrar": "d-none"}
    
    # Business rule: If patient has email, assume doctor is filling the form digitally
    # This triggers showing additional SUS form fields (campo 18) required for medical personnel
    if dados_paciente["email_paciente"] != "":
        dic["campo_18_mostrar"] = ""  # Show campo 18 fields
        dados_paciente["preenchido_por"] = "medico"  # Set form completion context
    
    # Legal requirement: If patient is incapable, must show responsible person field
    if dados_paciente["incapaz"]:
        dic["responsavel_mostrar"] = ""  # Show responsible person name field
    
    return dic, dados_paciente


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field

# Constants for form choices
REPETIR_ESCOLHAS = [(True, "Sim"), (False, "Não")]


# pre process
class PreProcesso(forms.Form):
    cpf_paciente = forms.CharField(
        required=True, 
        label="", 
        max_length=14,
        error_messages={'required': 'Por favor, insira o CPF do paciente.'}
    )
    cid = forms.CharField(
        required=True, 
        label="",
        error_messages={'required': 'Por favor, insira o CID da doença.'}
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.attrs = {'novalidate': True}
        self.helper.form_show_errors = False  # Don't show inline error messages
        self.helper.error_text_inline = False  # Don't show error text but keep visual indicators
        self.helper.layout = Layout(
            Field('cpf_paciente', css_class='form-control'),
            Field('cid', css_class='form-control'),
            Submit('submit', 'Buscar', css_class='btn btn-primary')
        )

    def clean_cid(self):
        cid = self.cleaned_data["cid"].upper()
        doencas = Doenca.objects.all()
        lista_cids = []
        for doenca in doencas:
            lista_cids.append(doenca.cid)
        if cid not in lista_cids:
            raise forms.ValidationError(f'CID "{cid}" incorreto!')
        return cid

    def clean_cpf_paciente(self):
        cpf_paciente = self.cleaned_data["cpf_paciente"]
        if not isCpfValid(cpf_paciente):
            raise forms.ValidationError(f"CPF {cpf_paciente} inválido!")
        return cpf_paciente


# new process
class NovoProcesso(forms.Form):
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
        self.helper.add_input(Submit("submit", "Salvar Processo", css_class="btn btn-primary"))

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

    # Dados do paciente
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
    incapaz = forms.ChoiceField(
        choices=((False, "Não"), (True, "Sim")),
        label="É incapaz?",
        initial=False,
        widget=forms.RadioSelect(attrs={"class": "form-check-inline"}),
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
    anamnese = forms.CharField(required=True, label="Anamnese", error_messages={'required': 'Por favor, insira a anamnese.'})
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
        input_formats=[
            "%d/%m/%Y",
        ],
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

    # validate form data
    def clean(self):
        """
        Custom form validation that handles medications submitted in POST request.
        FIRST: Extract all submitted med_ids
        THEN: For each submitted med_id, validate that ALL required fields are filled
        FINALLY: Remove validation errors only for medications not submitted at all
        
        Critique:
        - This method is extremely complex (100+ lines) and violates SRP
        - Mixes validation logic with logging and debugging code
        - Hardcoded medication field names (med1-med4) reduce maintainability
        - Complex nested loops and conditionals make it hard to test
        - Heavy use of logger in validation logic suggests debugging code left in production
        
        Suggested Improvements:
        - Extract medication validation to separate MedicationValidator class
        - Create clean_medication_field() helper methods for each medication
        - Remove debugging logger calls from production validation code
        - Use configuration-driven field validation instead of hardcoded loops
        - Add unit tests for each validation scenario
        - Consider using Django's formsets for dynamic medication handling
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info("=== DEBUG: Form validation starting ===")
        logger.info(f"Form errors before custom validation: {dict(self.errors)}")
        
        cleaned_data = super().clean()
        
        # Check which medications were actually submitted
        submitted_fields = set(self.data.keys()) if self.data else set()
        logger.info(f"Submitted fields: {submitted_fields}")
        
        # FIRST: Extract all submitted med_ids
        submitted_med_ids = []
        for i in range(1, 5):
            med_id_field = f"id_med{i}"
            if med_id_field in submitted_fields:
                med_id_value = self.data.get(med_id_field)
                # Check for various forms of "empty" medication selections
                is_empty_medication = (
                    not med_id_value or 
                    not med_id_value.strip() or 
                    med_id_value.strip().lower() in ["nenhum", "none", "", "null", "undefined"]
                )
                if not is_empty_medication:  # Non-empty value and not "nenhum" variants
                    submitted_med_ids.append(i)
                    logger.info(f"Found submitted medication {i}: {med_id_value}")
                else:
                    logger.info(f"Medication {i} has value '{med_id_value}' - treating as not submitted")
        
        logger.info(f"Total submitted medications: {submitted_med_ids}")
        
        # CRITICAL CHECK: At least one medication must be submitted
        if not submitted_med_ids:
            self.add_error(None, "Pelo menos um medicamento deve ser selecionado.")
            logger.info("VALIDATION ERROR: No medications submitted - form is invalid")
            return cleaned_data  # Exit early - form is invalid
        
        # THEN: For each submitted med_id, validate ALL required fields are filled
        for i in submitted_med_ids:
            logger.info(f"Validating all fields for submitted medication {i}")
            
            # Check main medication field
            med_id_field = f"id_med{i}"
            med_id_value = self.data.get(med_id_field)
            if not med_id_value or not med_id_value.strip():
                self.add_error(None, f"Medicamento {i}: Seleção do medicamento é obrigatória")
                logger.info(f"Added med_id error for medication {i}")
            
            # Check repetir posologia field
            repetir_field = f"med{i}_repetir_posologia"
            has_repetir_error = False
            if repetir_field not in submitted_fields:
                has_repetir_error = True
                logger.info(f"Missing {repetir_field}")
            
            if has_repetir_error:
                self.add_error(None, f"Medicamento {i}: Campo 'repetir posologia' deve ser preenchido")
                logger.info(f"Added repetir error for medication {i}")
            
            # Check dosage and quantity fields for all 6 months
            has_missing_fields = False
            for month in range(1, 7):
                posologia_field = f"med{i}_posologia_mes{month}"
                qtd_field = f"qtd_med{i}_mes{month}"
                
                # Check posologia field
                if posologia_field not in submitted_fields:
                    has_missing_fields = True
                    logger.info(f"Missing {posologia_field}")
                else:
                    posologia_value = self.data.get(posologia_field)
                    if not posologia_value or not posologia_value.strip():
                        has_missing_fields = True
                        logger.info(f"Empty {posologia_field}")
                
                # Check quantity field
                if qtd_field not in submitted_fields:
                    has_missing_fields = True
                    logger.info(f"Missing {qtd_field}")
                else:
                    qtd_value = self.data.get(qtd_field)
                    if not qtd_value or not qtd_value.strip():
                        has_missing_fields = True
                        logger.info(f"Empty {qtd_field}")
            
            # Add single summary error message if any fields are missing/invalid
            if has_missing_fields:
                self.add_error(None, f"Medicamento {i}: Todos os campos de posologia e quantidade (6 meses) devem ser preenchidos")
                logger.info(f"Added summary error for medication {i}")
        
        # FINALLY: Remove validation errors only for medications not submitted at all
        for i in range(1, 5):
            if i not in submitted_med_ids:
                logger.info(f"Medication {i} not submitted, removing validation errors")
                
                # Remove errors for main medication fields
                med_id_field = f"id_med{i}"
                if med_id_field in self.errors:
                    logger.info(f"Removing error for {med_id_field}")
                    del self.errors[med_id_field]
                
                repetir_field = f"med{i}_repetir_posologia"
                if repetir_field in self.errors:
                    logger.info(f"Removing error for {repetir_field}")
                    del self.errors[repetir_field]
                
                # Remove errors for dosage and quantity fields
                for month in range(1, 7):
                    posologia_field = f"med{i}_posologia_mes{month}"
                    qtd_field = f"qtd_med{i}_mes{month}"
                    
                    if posologia_field in self.errors:
                        logger.info(f"Removing error for {posologia_field}")
                        del self.errors[posologia_field]
                    if qtd_field in self.errors:
                        logger.info(f"Removing error for {qtd_field}")
                        del self.errors[qtd_field]
        
        logger.info(f"Form errors after custom validation: {dict(self.errors)}")
        logger.info("=== DEBUG: Form validation complete ===")
        
        return cleaned_data

    # save prescription process
    @transaction.atomic
    def save(self, usuario, medico, meds_ids):
        """
        Saves a new prescription process to the database.
        
        This method handles the complex business logic of creating a new
        medical prescription process, including patient creation/retrieval,
        process creation, and medication associations.
        
        Args:
            usuario (User): The authenticated user (doctor)
            medico (Medico): The doctor's profile
            meds_ids (list): List of medication IDs to associate
            
        Returns:
            int: The ID of the created process
            
        Critique:
        - Method is too long and handles multiple responsibilities
        - Mixes patient management with process creation logic
        - Hardcoded field mappings reduce maintainability
        - No validation of business rules (e.g., duplicate processes)
        - Error handling is minimal for database operations
        
        Suggested Improvements:
        - Extract patient creation/retrieval to PatientService
        - Create ProcessBuilder class to handle process creation
        - Add validation for duplicate patient/disease combinations
        - Implement proper error handling and rollback strategies
        - Add audit logging for medical prescription creation
        - Consider using Django model managers for complex queries
        """
        dados = self.cleaned_data
        clinica_id = dados["clinicas"]
        doenca = Doenca.objects.get(cid=dados["cid"])
        cpf_paciente = dados["cpf_paciente"]

        emissor = Emissor.objects.get(medico=medico, clinica_id=clinica_id)

        patient_repo = PatientRepository()
        paciente_existe = patient_repo.check_patient_exists(cpf_paciente)

        registration_service = ProcessRegistrationService()
        processo_id = registration_service.register_process(
            dados, meds_ids, doenca, emissor, usuario, paciente_existe=paciente_existe
        )

        return processo_id


# renew process
class RenovarProcesso(NovoProcesso):
    edicao_completa = forms.ChoiceField(
        required=True,
        initial=False,
        choices=[(False, "Não"), (True, "Sim")],
        widget=forms.RadioSelect(attrs={"class": "form-check-inline"}),
        error_messages={'required': 'Por favor, selecione uma opção.'}
    )

    @transaction.atomic
    def save(self, usuario, medico, processo_id, meds_ids):
        dados = self.cleaned_data
        edicao_completa = dados["edicao_completa"]

        if edicao_completa == "True":
            cpf_paciente = dados["cpf_paciente"]
            patient_repo = PatientRepository()
            paciente_existe = patient_repo.check_patient_exists(cpf_paciente)
            clinica_id = dados["clinicas"]
            doenca = Doenca.objects.get(cid=dados["cid"])
            emissor = Emissor.objects.get(medico=medico, clinica_id=clinica_id)

            registration_service = ProcessRegistrationService()
            registration_service.register_process(
                dados,
                meds_ids,
                doenca,
                emissor,
                usuario,
                paciente_existe=paciente_existe,
                cid=dados["cid"],
                processo_id=processo_id,  # Pass the specific process being edited
            )
        else:
            # Partial renewal - update only the date
            processo = Processo.objects.get(id=processo_id)
            processo.prescricao[1]['data_1'] = dados['data_1'] 
            processo.save(update_fields=['prescricao'])
            
            registration_service = ProcessRegistrationService()
            registration_service._associate_medications(processo, meds_ids)


# extract conditional fields
def extrair_campos_condicionais(formulario):
    campos_condicionais = []
    for campo in formulario:
        if campo.name[0:4] == "opt_":
            campos_condicionais.append(campo)
    return campos_condicionais


# fabricate form
def fabricar_formulario(cid, renovar):
    if renovar:
        modelo_base = RenovarProcesso
    else:
        modelo_base = NovoProcesso

    protocolo = Protocolo.objects.get(doenca__cid=cid)

    # Try new data-driven approach first, fallback to empty fields for unmigrated protocols
    campos = get_conditional_fields(protocolo)
    if not campos:
        # Legacy protocols without data-driven configuration will have no conditional fields
        # This maintains backward compatibility until all protocols are migrated
        campos = {}
        logger.debug(f"No conditional fields configured for {protocolo.nome} - protocol needs migration")
    else:
        logger.debug(f"Using data-driven conditional fields for {protocolo.nome}")

    return type("SuperForm", (modelo_base,), campos)
