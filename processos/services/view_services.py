"""
View Services - Setup and Data Preparation for Views

This module provides services that handle the complex setup logic for prescription views.
These services extract the heavy lifting from views, making them thin controllers that
focus only on HTTP concerns.

Services:
- PrescriptionViewSetupService: Handles all setup logic for prescription views
"""

import logging
from typing import Optional, List, Tuple, Any, Union
from datetime import date

from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import QuerySet

from medicos.seletor import medico as seletor_medico
from processos.models import Processo, Doenca
from processos.repositories.medication_repository import MedicationRepository
from processos.repositories.process_repository import ProcessRepository
from processos.services.prescription_services import RenewalService
from processos.forms import fabricar_formulario
from django.forms.models import model_to_dict
from pacientes.models import Paciente
from processos.services.view_setup_models import (
    ViewSetupResult, SetupError, ViewSetupSuccess,
    CommonSetupData, PrescriptionFormData, 
    NewPrescriptionData, EditPrescriptionData,
    is_setup_error, is_setup_success
)


logger = logging.getLogger(__name__)


class PrescriptionViewSetupService:
    """
    Service for setting up prescription views (cadastro and edicao).
    
    Handles all the complex setup logic that views currently do:
    - User and doctor validation
    - Session state validation
    - Clinic choices preparation
    - Dynamic form construction
    - Initial data preparation
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def setup_for_new_prescription(self, request) -> ViewSetupResult:
        """
        Set up all data needed for the cadastro (new prescription) view.
        
        Args:
            request: Django HTTP request object
            
        Returns:
            ViewSetupResult: Contains all setup data or error information
        """
        try:
            print(f"DEBUG SETUP: ============= SETUP SERVICE CALLED =============")
            print(f"DEBUG SETUP: Starting setup_for_new_prescription for user: {request.user}")
            self.logger.info(f"Setting up new prescription view for user: {request.user}")
            
            # Step 1: Common setup (user, doctor, clinics)
            print(f"DEBUG SETUP: Calling _setup_common_data")
            common_result = self._setup_common_data(request)
            print(f"DEBUG SETUP: Common setup result: {type(common_result)}")
            if isinstance(common_result, SetupError):
                return common_result
            
            # Step 2: Validate new prescription session requirements
            session_error = self._validate_new_prescription_session(request)
            if session_error:
                return session_error
            
            # Step 3: Get prescription-specific data
            paciente_existe = request.session["paciente_existe"]
            primeira_data = date.today().strftime("%d/%m/%Y")
            cid = request.session["cid"]
            
            # Step 4: Get medications and form for new prescription
            med_repo = MedicationRepository()
            medicamentos = med_repo.list_medications_by_cid(cid)
            ModeloFormulario = fabricar_formulario(cid, False)  # False = new prescription
            
            # Step 5: Prepare initial data based on patient existence
            try:
                dados_iniciais = self._prepare_initial_form_data(request, paciente_existe, primeira_data, cid)
            except KeyError as e:
                self.logger.error(f"Missing session data for initial data: {e}")
                return SetupError(
                    message=str(e),
                    redirect_to="home"
                )
            
            self.logger.info(f"Successfully set up new prescription view for CID: {cid}")
            
            return ViewSetupSuccess(
                common=common_result,
                form=PrescriptionFormData(
                    cid=cid,
                    medicamentos=medicamentos,
                    ModeloFormulario=ModeloFormulario
                ),
                specific=NewPrescriptionData(
                    paciente_existe=paciente_existe,
                    primeira_data=primeira_data,
                    dados_iniciais=dados_iniciais
                )
            )
            
        except Exception as e:
            self.logger.error(f"Error setting up new prescription view: {e}", exc_info=True)
            return SetupError(
                message=f"Erro ao carregar dados do cadastro: {e}",
                redirect_to="home"
            )
    
    def setup_for_edit_prescription(self, request) -> ViewSetupResult:
        """
        Set up all data needed for the edicao (edit prescription) view.
        
        Args:
            request: Django HTTP request object
            
        Returns:
            ViewSetupResult: Contains all setup data or error information
        """
        try:
            self.logger.info(f"Setting up edit prescription view for user: {request.user}")
            
            # Step 1: Common setup (user, doctor, clinics)
            common_result = self._setup_common_data(request)
            if isinstance(common_result, SetupError):
                return common_result
            
            # Step 2: Validate edit prescription session requirements
            session_error = self._validate_edit_prescription_session(request, common_result.usuario)
            if session_error:
                return session_error
            
            # Step 3: Get edit-specific data
            cid = request.session["cid"]
            processo_id = int(request.session["processo_id"])
            from ..services.prescription.process_service import ProcessService
            process_service = ProcessService()
            processo = process_service.get_process_by_id_and_user(processo_id, common_result.usuario)
            
            # Step 4: Get medications and form for edit
            med_repo = MedicationRepository()
            medicamentos = med_repo.list_medications_by_cid(cid)
            ModeloFormulario = fabricar_formulario(cid, True)  # True = edit/renewal form
            
            # Step 5: Get first date and prepare initial data from existing process
            try:
                primeira_data = request.session.get("data1", date.today().strftime("%d/%m/%Y"))
            except KeyError:
                primeira_data = date.today().strftime("%d/%m/%Y")
                self.logger.info(f"Using default primeira_data: {primeira_data}")
            
            # Create initial data from existing process with user's versioned data
            renewal_service = RenewalService()
            dados_iniciais = renewal_service.create_renewal_dictionary(processo, user=common_result.usuario)
            dados_iniciais["clinicas"] = dados_iniciais["clinica"].id
            dados_iniciais = renewal_service._retrieve_prescription_data(dados_iniciais, processo)
            # Override any data_1 from stored prescription with session date (in correct BR format)
            dados_iniciais["data_1"] = primeira_data
            
            self.logger.info(f"Successfully set up edit prescription view for process: {processo_id}")
            
            return ViewSetupSuccess(
                common=common_result,
                form=PrescriptionFormData(
                    cid=cid,
                    medicamentos=medicamentos,
                    ModeloFormulario=ModeloFormulario
                ),
                specific=EditPrescriptionData(
                    processo_id=processo_id,
                    processo=processo,
                    dados_iniciais=dados_iniciais
                )
            )
            
        except Exception as e:
            self.logger.error(f"Error setting up edit prescription view: {e}", exc_info=True)
            return SetupError(
                message=f"Erro na inicialização: {e}",
                redirect_to="processos-busca"
            )
    
    def _setup_common_data(self, request) -> Union[SetupError, CommonSetupData]:
        """Set up data common to both cadastro and edicao views."""
        try:
            print(f"DEBUG COMMON: Starting common setup for user: {request.user}")
            # Get user and doctor
            usuario = request.user
            medico = seletor_medico(usuario)
            print(f"DEBUG COMMON: Got medico: {medico}")
            
            # Check if medico exists
            if not medico:
                print(f"DEBUG COMMON: No medico found, redirecting to home")
                self.logger.error(f"No doctor profile found for user: {usuario}")
                return SetupError(
                    message="Erro: perfil médico não encontrado. Contate o suporte.",
                    redirect_to="home"
                )
            
            # Get clinics and create choices
            clinicas = medico.clinicas.all()
            escolhas = self._create_clinic_choices(clinicas, usuario)
            
            self.logger.debug(f"Common setup complete - User: {usuario}, Clinics: {clinicas.count()}")
            
            return CommonSetupData(
                usuario=usuario,
                medico=medico,
                clinicas=clinicas,
                escolhas=escolhas
            )
            
        except Exception as e:
            self.logger.error(f"Error in common setup: {e}", exc_info=True)
            return SetupError(
                message=f"Erro ao carregar dados básicos: {e}",
                redirect_to="home"
            )
    
    def _prepare_initial_form_data(self, request, paciente_existe: bool, primeira_data: str, cid: str) -> dict:
        """
        Constructs initial form data based on patient existence and session context.
        
        This method handles two distinct scenarios in Brazilian medical prescription workflow:
        1. Existing patient: Pre-populate form with patient data from database
        2. New patient: Initialize form with minimal data from session (CPF + disease info)
        
        The function bridges the gap between session-based workflow state and form initialization,
        ensuring data consistency across the multi-step prescription process.
        
        Args:
            request: HTTP request containing session data
            paciente_existe (bool): Whether patient exists in doctor's database
            primeira_data (str): Default date for prescription
            cid (str): Disease CID code
        
        Returns:
            dict: Form initial data dictionary
        
        Raises:
            KeyError: If required session data is missing (indicates broken workflow)
        """
        if paciente_existe:
            # Patient exists - load full patient data from database
            if "paciente_id" not in request.session:
                raise KeyError("ID do paciente não encontrado na sessão.")
            
            paciente_id = request.session["paciente_id"]
            from ..repositories.patient_repository import PatientRepository
            patient_repo = PatientRepository()
            paciente = patient_repo.get_patient_by_id(paciente_id)
            
            # Get user's versioned data for form initialization
            user = request.user
            version = paciente.get_version_for_user(user)
            
            if version:
                # Use versioned data for form initialization
                dados_paciente = model_to_dict(version)
                # Keep master record fields that aren't versioned
                dados_paciente['id'] = paciente.id
                dados_paciente['cpf_paciente'] = paciente.cpf_paciente
                dados_paciente['usuarios'] = paciente.usuarios.all()
            else:
                # Fallback to master record if no version found
                dados_paciente = model_to_dict(paciente)
            
            # Add prescription-specific data not stored in patient model
            from ..repositories.domain_repository import DomainRepository
            domain_repo = DomainRepository()
            disease = domain_repo.get_disease_by_cid(cid)
            dados_paciente["diagnostico"] = disease.nome
            dados_paciente["cid"] = cid
            dados_paciente["data_1"] = primeira_data
            
            self.logger.debug(f"Prepared initial data for existing patient {paciente_id}")
            return dados_paciente
        else:
            # New patient - minimal form initialization with session data
            if "cpf_paciente" not in request.session:
                raise KeyError("CPF do paciente não encontrado na sessão.")
            
            # Get domain repository for disease lookup
            from ..repositories.domain_repository import DomainRepository
            domain_repo = DomainRepository()
            disease = domain_repo.get_disease_by_cid(cid)
            
            # Return minimal data structure for new patient form
            dados_iniciais = {
                "cpf_paciente": request.session["cpf_paciente"],
                "data_1": primeira_data,
                "cid": cid,
                "diagnostico": disease.nome,
            }
            
            self.logger.debug(f"Prepared initial data for new patient with CPF {request.session['cpf_paciente']}")
            return dados_iniciais
    
    def _create_clinic_choices(self, clinicas: QuerySet, usuario) -> Tuple:
        """Create clinic choices tuple with versioned names."""
        escolhas = []
        for c in clinicas:
            version = c.get_version_for_user(usuario)
            clinic_name = version.nome_clinica if version else c.nome_clinica
            escolhas.append((c.id, clinic_name))
        return tuple(escolhas)
    
    def _validate_new_prescription_session(self, request) -> Optional[SetupError]:
        """Validate session state for new prescription."""
        # Check for required session variables
        if "paciente_existe" not in request.session:
            self.logger.error("Missing paciente_existe in session")
            return SetupError(
                message="Sessão expirada. Por favor, inicie o cadastro novamente.",
                redirect_to="home"
            )
        
        if "cid" not in request.session:
            self.logger.error("Missing cid in session")
            return SetupError(
                message="CID não encontrado na sessão. Por favor, selecione o diagnóstico novamente.",
                redirect_to="home"
            )
        
        return None  # Success - no error
    
    def _validate_edit_prescription_session(self, request, usuario) -> Optional[SetupError]:
        """Validate session state for edit prescription."""
        # Check for required session variables
        if "cid" not in request.session:
            self.logger.error("Missing cid in session for edit")
            return SetupError(
                message="Erro na inicialização: CID não encontrado na sessão.",
                redirect_to="processos-busca"
            )
        
        if "processo_id" not in request.session:
            self.logger.error("Missing processo_id in session for edit")
            return SetupError(
                message="Processo não encontrado ou você não tem permissão para acessá-lo.",
                redirect_to="processos-busca"
            )
        
        # Verify user owns this process
        try:
            processo_id = int(request.session["processo_id"])
            from ..services.prescription.process_service import ProcessService
            process_service = ProcessService()
            processo = process_service.get_process_by_id_and_user(processo_id, usuario)
            self.logger.debug(f"Process {processo_id} found and owned by user")
            return None  # Success - no error
            
        except (KeyError, ValueError, Processo.DoesNotExist) as e:
            self.logger.error(f"Error validating process ownership: {e}")
            return SetupError(
                message="Processo não encontrado ou você não tem permissão para acessá-lo.",
                redirect_to="processos-busca"
            )
    
    def setup_process_for_editing(self, process_id: str, user, request) -> ViewSetupResult:
        """
        Set up process selection for editing workflow.
        
        Handles the business logic of selecting a process for editing, including:
        - Process authorization validation
        - Session state setup
        - Data preparation for edicao view
        
        Args:
            process_id: The process ID to select
            user: The user attempting to select the process
            request: Django request object (for session management)
            
        Returns:
            ViewSetupResult: Success with redirect data or error information
        """
        try:
            self.logger.info(f"Setting up process {process_id} for editing by user {user.email}")
            
            # Use repository to get process with authorization check
            process_repo = ProcessRepository()
            processo, cid = process_repo.get_process_with_disease_info(int(process_id), user)
            
            if not processo:
                self.logger.warning(f"Process {process_id} not found or unauthorized for user {user.email}")
                return SetupError(
                    message="Processo não encontrado ou você não tem permissão para acessá-lo.",
                    redirect_to="processos-busca"
                )
            
            # Set up session state for editing workflow
            request.session["processo_id"] = process_id
            request.session["cid"] = cid
            
            self.logger.info(f"Successfully set up process {process_id} for editing")
            
            # Return success with process information
            return ViewSetupSuccess(
                common=None,  # Not needed for this workflow
                form=None,    # Not needed for this workflow  
                specific={
                    'processo': processo,
                    'success_message': f"Processo selecionado: {processo.doenca.nome}",
                    'redirect_to': "processos-edicao"
                }
            )
            
        except ValueError as e:
            self.logger.error(f"Invalid process ID {process_id}: {e}")
            return SetupError(
                message="ID do processo inválido.",
                redirect_to="processos-busca"
            )
        except Exception as e:
            self.logger.error(f"Error setting up process {process_id} for editing: {e}", exc_info=True)
            return SetupError(
                message="Erro interno ao selecionar processo.",
                redirect_to="processos-busca"
            )
    
    def setup_process_for_renewal_editing(self, process_id: str, user, request, nova_data: str) -> ViewSetupResult:
        """
        Set up process selection for renewal editing workflow.
        
        Similar to setup_process_for_editing but includes renewal date setup.
        
        Args:
            process_id: The process ID to select
            user: The user attempting to select the process
            request: Django request object (for session management)
            nova_data: The new date for renewal
            
        Returns:
            ViewSetupResult: Success with redirect data or error information
        """
        try:
            self.logger.info(f"Setting up process {process_id} for renewal editing by user {user.email}")
            
            # Use repository to get process with authorization check
            process_repo = ProcessRepository()
            processo, cid = process_repo.get_process_with_disease_info(int(process_id), user)
            
            if not processo:
                self.logger.warning(f"Process {process_id} not found or unauthorized for user {user.email}")
                return SetupError(
                    message="Processo não encontrado ou você não tem permissão para acessá-lo.",
                    redirect_to="processos-renovacao-rapida"
                )
            
            # Set up session state for renewal editing workflow
            request.session["processo_id"] = process_id
            request.session["cid"] = cid
            # Convert date object to string for JSON serialization
            if hasattr(nova_data, 'strftime'):
                request.session["data1"] = nova_data.strftime("%d/%m/%Y")
            else:
                request.session["data1"] = str(nova_data)
            
            self.logger.info(f"Successfully set up process {process_id} for renewal editing")
            
            # Return success with process information
            return ViewSetupSuccess(
                common=None,  # Not needed for this workflow
                form=None,    # Not needed for this workflow
                specific={
                    'processo': processo,
                    'redirect_to': "processos-edicao"
                }
            )
            
        except ValueError as e:
            self.logger.error(f"Invalid process ID {process_id}: {e}")
            return SetupError(
                message="ID do processo inválido.",
                redirect_to="processos-renovacao-rapida"
            )
        except Exception as e:
            self.logger.error(f"Error setting up process {process_id} for renewal editing: {e}", exc_info=True)
            return SetupError(
                message="Erro interno ao selecionar processo.",
                redirect_to="processos-renovacao-rapida"
            )
    
    def validate_doctor_profile_completeness(self, medico, usuario) -> Optional[SetupError]:
        """
        Validate that doctor has completed required profile information.
        
        This method implements business rules about doctor profile completion
        requirements before allowing prescription creation.
        
        Args:
            medico: The doctor's profile
            usuario: The user (for clinic access check)
            
        Returns:
            SetupError: If profile is incomplete, with appropriate redirect
            None: If profile is complete and valid
        """
        self.logger.debug(f"Validating doctor profile completeness for medico {medico.id if medico else 'None'}")
        
        # Check if doctor has required CRM and CNS data
        if not medico.crm_medico or not medico.cns_medico:
            self.logger.info(f"Doctor profile incomplete - missing CRM or CNS data")
            return SetupError(
                message="Complete seus dados médicos antes de criar processos.",
                redirect_to="complete-profile"
            )
        
        # Check if doctor has at least one clinic registered
        if not usuario.clinicas.exists():
            self.logger.info(f"Doctor profile incomplete - no clinics registered")
            return SetupError(
                message="Cadastre uma clínica antes de criar processos.",
                redirect_to="clinicas-cadastro"
            )
        
        self.logger.debug(f"Doctor profile validation passed for medico {medico.id}")
        return None  # Profile is complete
    
    def build_patient_search_context(self, usuario, busca_param: Optional[str] = None) -> dict:
        """
        Build standardized context for patient search and listing operations.
        
        This method consolidates the duplicate context building patterns found in:
        - busca_processos (GET)
        - renovacao_rapida (GET and error handling)
        
        Creates optimized patient queries with prefetch_related for performance.
        
        Args:
            usuario: The authenticated user
            busca_param: Optional search parameter for filtering patients
            
        Returns:
            dict: Standard context dictionary with patient data
        """
        self.logger.debug(f"Building patient search context for user {usuario.email}")
        
        # OPTIMIZATION: Prefetch related usuarios to avoid N+1 queries
        # Before: 1 + N queries (1 for patients, N for each patient's users)
        # After: 1 query with JOIN
        pacientes_usuario = usuario.pacientes.prefetch_related('usuarios').all()
        
        # Handle patient search if busca parameter provided
        if busca_param:
            from pacientes.models import Paciente
            patient_results = Paciente.get_patients_for_user_search(usuario, busca_param)
            busca_pacientes = [patient for patient, version in patient_results]
        else:
            busca_pacientes = []
        
        context = {
            "pacientes_usuario": pacientes_usuario,
            "busca_pacientes": busca_pacientes,
            "usuario": usuario
        }
        
        self.logger.debug(f"Built context with {pacientes_usuario.count()} total patients, {len(busca_pacientes)} search results")
        return context
    
    def extract_conditional_fields(self, form) -> list:
        """
        Extract conditional fields from a form based on field name patterns.
        
        This method identifies fields that are conditionally displayed
        based on the 'opt_' prefix naming convention.
        
        Args:
            form: Django form instance
            
        Returns:
            list: List of conditional form fields
        """
        return [field for field in form if field.name.startswith("opt_")]
    
    def adjust_conditional_fields(self, patient_data: dict) -> tuple:
        """
        Conditionally shows/hides form fields based on patient data and form completion context.
        
        This method implements complex business logic for Brazilian medical form regulations:
        1. If patient has email, it means the form is being filled digitally by a doctor (not patient)
        2. If patient is incapable (incapaz), a responsible person's name field must be shown
        3. Campo 18 refers to specific SUS (Brazilian health system) form fields that are only
           required when the form is filled by medical personnel rather than the patient
        
        Args:
            patient_data (dict): Patient data dictionary containing form field values
        
        Returns:
            tuple: (visibility_dict, modified_patient_data)
                - visibility_dict: CSS classes to show/hide conditional fields
                - modified_patient_data: Updated patient data with 'preenchido_por' field set
        """
        # Initialize all conditional fields as hidden by default
        visibility_classes = {"responsavel_mostrar": "d-none", "campo_18_mostrar": "d-none"}
        
        # Business rule: If patient has email, assume doctor is filling the form digitally
        # This triggers showing additional SUS form fields (campo 18) required for medical personnel
        if patient_data.get("email_paciente", "") != "":
            visibility_classes["campo_18_mostrar"] = ""  # Show campo 18 fields
            patient_data["preenchido_por"] = "medico"  # Set form completion context
        
        # Legal requirement: If patient is incapable, must show responsible person field
        if patient_data.get("incapaz", False):
            visibility_classes["responsavel_mostrar"] = ""  # Show responsible person name field
        
        return visibility_classes, patient_data
    
    def get_medication_display_classes(self, show_existing_medications: bool, process=None) -> dict:
        """
        Dynamically controls medication tab visibility in the UI based on existing process data.
        
        This method determines which medication tabs should be visible in the form interface.
        By default, all medication tabs except the first one are hidden (using Bootstrap's 'd-none' class).
        When editing an existing process, this method reveals tabs for medications that are already
        associated with the process, ensuring users can see and edit existing medication data.
        
        Args:
            show_existing_medications (bool): Whether to show medications (True for editing existing process, False for new)
            process: Process instance when show_existing_medications=True
        
        Returns:
            dict: CSS class mapping for medication tabs ('d-none' to hide, '' to show)
        """
        # Initialize all medication tabs as hidden except med1 (which is always shown)
        display_classes = {
            "med2_mostrar": "d-none",
            "med3_mostrar": "d-none", 
            "med4_mostrar": "d-none",
        }
        
        if show_existing_medications and process:
            # Exact same logic as original mostrar_med function
            n = 1
            # Iterate through existing medications and reveal corresponding tabs
            # This ensures users can see all medications already associated with the process
            for med in process.medicamentos.all():
                display_classes[f"med{n}_mostrar"] = ""  # Remove 'd-none' class to show the tab
                n = n + 1
        
        return display_classes
    
