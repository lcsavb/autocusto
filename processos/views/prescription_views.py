"""
Prescription Views - Medical Prescription Processing for Brazilian Healthcare System

This module contains Django views for managing medical prescriptions in a Brazilian healthcare context.
The application handles complex regulatory requirements for prescription documentation, patient data
management, and medical protocol compliance.

Key Business Context:
- Medical prescriptions must follow Brazilian regulatory standards (CID-10 disease codes)
- Patient data requires versioning per doctor to maintain data privacy between medical practices
- PDF generation creates legally compliant prescription documents
- Multi-step workflow supports both new patient registration and existing patient prescription updates

Architecture:
- Clean separation between HTTP concerns (views) and business logic (services)
- Service layer handles complex prescription workflow orchestration
- Repository pattern abstracts data access for patient and domain entities
- Error handling provides user-friendly feedback while maintaining system integrity
"""

import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.forms.models import model_to_dict
from pacientes.models import Paciente
from processos.models import Doenca
# Service-based architecture - views delegate business logic to specialized services
from processos.utils.url_utils import generate_protocol_link
from processos.services.view_services import PrescriptionViewSetupService
from processos.services.view_setup_models import SetupError
from processos.utils.pdf_json_response_helper import PDFJsonResponseHelper

logger = logging.getLogger(__name__)


@login_required
def edicao(request):
    """
    Handles editing of existing medical prescription processes in the Brazilian healthcare system.
    
    Business Context:
    - Allows doctors to modify previously created prescriptions while maintaining audit trail
    - Preserves patient data versioning to ensure privacy between different medical practices
    - Updates prescription data while regenerating compliant PDF documentation
    - Supports complex conditional form fields based on CID-10 disease codes and patient history
    
    HTTP Flow:
    - GET: Displays pre-populated form with existing prescription data
    - POST: Processes form submission, updates prescription, and generates new PDF
    
    Clean Architecture:
    - View handles only HTTP concerns (request/response, session, messages)
    - Business logic delegated to PrescriptionViewSetupService
    - Error handling provides user-friendly feedback with proper redirects
    """
    # Initialize service for prescription setup - centralizes complex initialization logic
    # This service handles doctor validation, patient data retrieval, form setup, and permissions
    setup_service = PrescriptionViewSetupService()
    setup = setup_service.setup_for_edit_prescription(request)
    
    # Early error handling - if setup fails, redirect user with clear feedback
    # Common failures: missing prescription ID, unauthorized access, invalid doctor profile
    if isinstance(setup, SetupError):
        messages.error(request, setup.message)
        return redirect(setup.redirect_to)
    
    # Extract validated setup data - service ensures all data is properly initialized
    # These objects are guaranteed to exist and be valid at this point
    usuario = setup.common.usuario          # Current authenticated user
    medico = setup.common.medico            # Doctor profile associated with user
    escolhas = setup.common.escolhas        # Form choice fields (clinics, medications, etc.)
    medicamentos = setup.form.medicamentos  # Available medications for this prescription type
    ModeloFormulario = setup.form.ModeloFormulario  # Dynamic form class based on CID-10 code
    processo = setup.specific.processo      # Existing prescription process being edited
    processo_id = setup.specific.processo_id # Database ID of the prescription

    # POST request: Form submission for prescription update
    # Delegate to helper function to maintain clean separation of concerns
    if request.method == "POST":
        return _handle_prescription_edit_post(request, setup, ModeloFormulario, escolhas, medicamentos, processo_id)
    
    # GET request: Display form with existing prescription data pre-populated
    # Form initialization uses existing prescription data to allow editing
    formulario = ModeloFormulario(escolhas, medicamentos, initial=setup.specific.dados_iniciais)
    
    # Extract conditional form fields - these are form fields that show/hide based on other selections
    # Important for medical forms where certain fields only apply to specific conditions or treatments
    setup_service_instance = PrescriptionViewSetupService()
    campos_condicionais = setup_service_instance.extract_conditional_fields(formulario)
    
    # Generate protocol link for medical reference - links to official Brazilian medical protocols
    # Based on CID-10 disease code to provide doctors with regulatory guidance
    link_protocolo = generate_protocol_link(setup.form.cid)

    # Build template context with all necessary data for rendering the edit form
    contexto = {
        "formulario": formulario,              # Pre-populated form ready for editing
        "processo": processo,                  # Existing prescription data for reference
        "campos_condicionais": campos_condicionais,  # JavaScript field visibility rules
        "link_protocolo": link_protocolo,      # Link to medical protocol documentation
    }
    
    # Add medication display configuration - determines which medication fields are shown
    # Different for editing (shows current medications) vs new prescriptions
    display_service = PrescriptionViewSetupService()
    contexto.update(display_service.get_medication_display_classes(True, processo))

    # Render the edit form template with all context data
    return render(request, "processos/edicao.html", contexto)


@login_required
def cadastro(request):
    """
    Handles registration of new medical prescriptions in the Brazilian healthcare system.
    
    Business Context:
    - Creates new prescription processes for patients (new or existing)
    - Supports complex workflow: patient search → prescription creation → PDF generation
    - Manages patient data versioning to maintain privacy between different doctors
    - Generates legally compliant prescription documents following Brazilian medical standards
    - Handles both scenarios: new patient registration and prescriptions for existing patients
    
    HTTP Flow:
    - GET: Displays prescription form (empty for new patients, pre-filled for existing)
    - POST: Processes form submission, creates prescription record, generates PDF
    
    Multi-step Workflow:
    1. Doctor selects CID-10 disease code (handled in previous view)
    2. Patient search/selection or new patient data entry
    3. Prescription form completion with medical details
    4. PDF generation and file storage
    5. Session management for workflow continuation
    
    Clean Architecture:
    - View focuses on HTTP concerns and workflow coordination
    - Business logic delegated to specialized services
    - Error handling provides clear user feedback
    """
    # Initialize prescription setup service - handles complex initialization workflow
    # Service validates doctor permissions, checks patient existence, prepares dynamic forms
    setup_service = PrescriptionViewSetupService()
    setup = setup_service.setup_for_new_prescription(request)
    
    # Early error handling with user-friendly feedback
    # Common setup failures: invalid session state, unauthorized access, missing doctor profile
    if isinstance(setup, SetupError):
        messages.error(request, setup.message)
        return redirect(setup.redirect_to)
    
    # Extract validated setup data - all objects guaranteed to exist and be properly initialized
    usuario = setup.common.usuario              # Authenticated user creating the prescription
    medico = setup.common.medico                # Doctor profile with validated credentials
    escolhas = setup.common.escolhas            # Dynamic form choices (clinics, medications)
    paciente_existe = setup.specific.paciente_existe  # Boolean: existing patient workflow
    medicamentos = setup.form.medicamentos     # Available medications for selected disease
    ModeloFormulario = setup.form.ModeloFormulario    # Dynamic form class based on CID-10
    
    # POST request: Form submission for new prescription creation
    # Delegate to specialized handler to maintain clean separation of concerns
    if request.method == "POST":
        return _handle_prescription_create_post(request, setup, ModeloFormulario, escolhas, medicamentos, paciente_existe)
    
    # GET request: Display prescription form for new prescription creation
    try:
        # Validate doctor profile completeness - ensures doctor can legally create prescriptions
        # Brazilian regulations require complete doctor registration including CRM number
        validation_service = PrescriptionViewSetupService()
        profile_error = validation_service.validate_doctor_profile_completeness(medico, usuario)
        
        # If doctor profile incomplete, redirect to profile completion with helpful message
        if profile_error:
            # Mark that we're in the setup flow for proper redirection after completion
            request.session['in_setup_flow'] = True
            messages.info(request, profile_error.message)
            return redirect(profile_error.redirect_to)
        
        # Initialize prescription form with appropriate initial data
        # For existing patients: pre-fill with versioned patient data
        # For new patients: provide empty form with disease-specific defaults
        formulario = ModeloFormulario(escolhas, medicamentos, initial=setup.specific.dados_iniciais)
        
        # Extract conditional form fields for dynamic UI behavior
        # Medical forms often have complex field dependencies based on disease type and patient history
        setup_service_instance = PrescriptionViewSetupService()
        campos_condicionais = setup_service_instance.extract_conditional_fields(formulario)
        
        # Generate link to official Brazilian medical protocols for reference
        # Helps doctors follow regulatory guidelines for the selected disease (CID-10)
        link_protocolo = generate_protocol_link(setup.form.cid)
        
        # Build base template context for prescription form rendering
        contexto = {
            "formulario": formulario,                    # Dynamic prescription form
            "paciente_existe": paciente_existe,          # Controls UI workflow (new vs existing patient)
            "campos_condicionais": campos_condicionais,  # JavaScript field visibility rules
            "link_protocolo": link_protocolo,            # Medical protocol reference link
        }
        
        # For existing patients: add patient data to context for form pre-population
        # Uses versioned patient data specific to this doctor to maintain privacy
        if paciente_existe:
            contexto.update(_get_patient_context_data(request, setup))
        
        # Add medication display configuration - controls which medication fields are shown
        # Different behavior for new prescriptions vs editing existing ones
        contexto.update(setup_service_instance.get_medication_display_classes(False))
        
        # Render prescription creation template with all necessary context
        return render(request, "processos/cadastro.html", contexto)
        
    except Exception as e:
        # Catch-all error handling for unexpected failures during form setup
        # Provides user feedback while logging technical details for debugging
        messages.error(request, f"Erro ao carregar formulário de cadastro: {e}")
        return redirect("home")


def _handle_prescription_edit_post(request, setup, ModeloFormulario, escolhas, medicamentos, processo_id):
    """
    Handles POST request for prescription editing - focuses on HTTP concerns and workflow coordination.
    
    Business Context:
    - Updates existing prescription while maintaining patient data privacy and audit trail
    - Regenerates PDF with updated prescription data following Brazilian medical standards
    - Preserves patient versioning to ensure data isolation between different doctors
    - Updates prescription database records and file storage atomically
    
    HTTP Workflow:
    1. Form validation and data extraction from POST request
    2. Business logic delegation to PrescriptionService for prescription update
    3. PDF generation and file storage through PDFFileService
    4. Session management for workflow continuation
    5. JSON response with success/failure status for AJAX frontend
    
    Error Handling:
    - Form validation errors: return structured JSON with field-specific error messages
    - Business logic errors: delegate to service layer, return user-friendly error responses
    - File I/O errors: handle PDF generation and storage failures gracefully
    - All errors logged for debugging while providing clean user feedback
    """
    # Import services locally to avoid circular dependencies and improve startup time
    from processos.services.prescription_services import PrescriptionService
    from processos.services.io_services import PDFFileService
    from processos.utils.pdf_json_response_helper import PDFJsonResponseHelper
    import os
    
    # Extract validated setup data from service initialization
    usuario = setup.common.usuario  # Authenticated user performing the update
    medico = setup.common.medico    # Doctor profile with update permissions
    
    # Initialize JSON response helper for consistent AJAX responses
    # Provides standardized success/error response format for frontend JavaScript
    json_response = PDFJsonResponseHelper()
    
    # STEP 1: Form validation and data extraction (HTTP concern)
    try:
        # Create form instance with POST data for validation
        # Form class is dynamically determined based on CID-10 disease code
        formulario = ModeloFormulario(escolhas, medicamentos, request.POST)
        
        # Validate form data according to medical prescription business rules
        # Returns structured error messages for frontend display if validation fails
        if not formulario.is_valid():
            return json_response.form_validation_failed(formulario.errors)
        
        # Extract cleaned form data - guaranteed to be valid and properly typed
        dados_formulario = formulario.cleaned_data
        
        # Retrieve selected clinic for prescription header information
        # Clinic selection is required for legally compliant prescription documents
        clinica = medico.clinicas.get(id=dados_formulario["clinicas"])
        
    except Exception as e:
        # Log technical details for debugging while providing user-friendly error message
        logger.error(f"Error in form processing: {str(e)}")
        return json_response.exception(e, context="validação do formulário")
    
    # STEP 2: Business logic delegation - prescription update and PDF generation
    try:
        # Delegate all business logic to PrescriptionService
        # Service handles: patient data versioning, prescription record update, PDF generation
        prescription_service = PrescriptionService()
        pdf_response, updated_processo_id = prescription_service.create_or_update_prescription(
            form_data=dados_formulario,      # Validated form data
            user=usuario,                    # User context for audit trail
            medico=medico,                   # Doctor performing the update
            clinica=clinica,                 # Clinic for prescription header
            patient_exists=True,             # Editing existing prescription (patient already exists)
            process_id=processo_id           # ID of prescription being updated
        )
        
        # Validate that business logic succeeded and returned expected results
        # Both PDF response and process ID are required for successful update
        if not pdf_response or not updated_processo_id:
            return json_response.pdf_generation_failed()
            
    except Exception as e:
        # Log business logic errors while providing user-friendly feedback
        logger.error(f"Error updating prescription: {str(e)}")
        return json_response.exception(e, context="atualização da prescrição")
    
    # STEP 3: File I/O and session management (HTTP concerns)
    try:
        # Save generated PDF to file system and get public URL
        # File service handles secure file storage with appropriate access controls
        file_service = PDFFileService()
        pdf_url = file_service.save_pdf_and_get_url(
            pdf_response,                                    # Generated PDF binary data
            dados_formulario.get('cpf_paciente', 'unknown'), # Patient CPF for file organization
            dados_formulario.get('cid', 'unknown')           # Disease code for file organization
        )
        
        # Validate that file storage succeeded
        if not pdf_url:
            return json_response.pdf_save_failed()
        
        # STEP 4: Session management for workflow continuation (HTTP concern)
        # Store critical workflow data in session for subsequent requests
        filename = os.path.basename(pdf_url.rstrip('/'))    # Extract filename for display
        request.session["path_pdf_final"] = pdf_url         # PDF URL for download/preview
        request.session["processo_id"] = updated_processo_id # Process ID for further operations
        
        # Log successful operation for audit trail and monitoring
        logger.info(f"Prescription updated successfully: Process {updated_processo_id}")
        
        # Return structured success response for AJAX frontend handling
        return json_response.success(
            pdf_url=pdf_url,                  # URL for PDF download/preview
            processo_id=updated_processo_id,  # Database ID for reference
            operation='update',               # Operation type for frontend logic
            filename=filename                 # Display filename for user feedback
        )
        
    except Exception as e:
        # Handle file I/O errors with detailed logging and user feedback
        logger.error(f"Error in file operations: {str(e)}")
        return json_response.exception(e, context="operações de arquivo")


def _handle_prescription_create_post(request, setup, ModeloFormulario, escolhas, medicamentos, paciente_existe):
    """
    Handles POST request for new prescription creation - focuses on HTTP concerns and workflow coordination.
    
    Business Context:
    - Creates new prescription records for patients (new or existing) in Brazilian healthcare system
    - Handles complex patient data versioning to maintain privacy between different doctors
    - Generates legally compliant prescription PDFs following Brazilian medical standards
    - Supports both workflows: new patient registration and prescriptions for existing patients
    - Maintains audit trail for all prescription creation activities
    
    HTTP Workflow:
    1. Form validation and data extraction from POST request
    2. Business logic delegation to PrescriptionService for prescription creation
    3. Patient record creation/update with proper data versioning
    4. PDF generation and secure file storage
    5. Session management for workflow continuation and success feedback
    6. JSON response with success/failure status for AJAX frontend
    
    Error Handling:
    - Form validation errors: return structured JSON with field-specific error messages
    - Business logic errors: delegate to service layer, return user-friendly error responses
    - File I/O errors: handle PDF generation and storage failures gracefully
    - Patient data conflicts: handle duplicate CPF and versioning edge cases
    - All errors logged for debugging while providing clean user feedback
    """
    # Import services locally to avoid circular dependencies and improve startup time
    from processos.services.prescription_services import PrescriptionService
    from processos.services.io_services import PDFFileService
    from processos.utils.pdf_json_response_helper import PDFJsonResponseHelper
    import os
    
    # Extract validated setup data from service initialization
    usuario = setup.common.usuario  # Authenticated user creating the prescription
    medico = setup.common.medico    # Doctor profile with creation permissions
    
    # Initialize JSON response helper for consistent AJAX responses
    # Provides standardized success/error response format for frontend JavaScript
    json_response = PDFJsonResponseHelper()
    
    # STEP 1: Form validation and data extraction (HTTP concern)
    try:
        # Create form instance with POST data for validation
        # Form class is dynamically determined based on CID-10 disease code selected earlier
        formulario = ModeloFormulario(escolhas, medicamentos, request.POST)
        
        # Validate form data according to medical prescription business rules
        # Includes validation for: patient data, medication dosages, clinic selection, etc.
        if not formulario.is_valid():
            return json_response.form_validation_failed(formulario.errors)
        
        # Extract cleaned and validated form data - guaranteed to be properly typed
        dados_formulario = formulario.cleaned_data
        
        # Retrieve selected clinic for prescription header information
        # Clinic data is required for legally compliant prescription documents in Brazil
        clinica = medico.clinicas.get(id=dados_formulario["clinicas"])
        
    except Exception as e:
        # Log technical details for debugging while providing user-friendly error message
        logger.error(f"Error in form processing: {str(e)}")
        return json_response.exception(e, context="validação do formulário")
    
    # STEP 2: Business logic delegation - prescription creation and patient management
    try:
        # Delegate all complex business logic to PrescriptionService
        # Service handles:
        # - Patient record creation/update with proper versioning
        # - Prescription record creation with medical data validation
        # - PDF generation following Brazilian prescription standards
        # - Data privacy enforcement between different medical practices
        prescription_service = PrescriptionService()
        pdf_response, processo_id = prescription_service.create_or_update_prescription(
            form_data=dados_formulario,      # Validated form data with patient and prescription info
            user=usuario,                    # User context for audit trail and permissions
            medico=medico,                   # Doctor creating the prescription
            clinica=clinica,                 # Clinic for prescription header and legal compliance
            patient_exists=paciente_existe,  # Boolean flag: existing patient vs new patient workflow
            process_id=None                  # None for new prescriptions (vs update operations)
        )
        
        # Validate that business logic succeeded and returned expected results
        # Both PDF response and process ID are critical for successful prescription creation
        if not pdf_response or not processo_id:
            return json_response.pdf_generation_failed()
            
    except Exception as e:
        # Log business logic errors while providing user-friendly feedback
        # Service layer should handle most business rule violations and provide clear error messages
        logger.error(f"Error creating prescription: {str(e)}")
        return json_response.exception(e, context="criação da prescrição")
    
    # STEP 3: File I/O and storage management (HTTP concerns)
    try:
        # Save generated PDF to file system with organized directory structure
        # File service handles: secure storage, access controls, and URL generation
        file_service = PDFFileService()
        pdf_url = file_service.save_pdf_and_get_url(
            pdf_response,                                    # Generated PDF binary data
            dados_formulario.get('cpf_paciente', 'unknown'), # Patient CPF for file organization
            dados_formulario.get('cid', 'unknown')           # Disease code for file categorization
        )
        
        # Validate that file storage succeeded before proceeding
        if not pdf_url:
            return json_response.pdf_save_failed()
        
        # STEP 4: Session management for workflow continuation (HTTP concern)
        # Store critical workflow data in session for subsequent requests
        # Used for: prescription preview, download links, workflow navigation
        filename = os.path.basename(pdf_url.rstrip('/'))  # Extract filename for user display
        request.session["processo_id"] = processo_id      # Store process ID for further operations
        
        # Log successful operation for audit trail and system monitoring
        logger.info(f"Prescription created successfully: Process {processo_id}")
        
        # Return structured success response for AJAX frontend handling
        # Frontend uses this data to: show success message, enable PDF download, navigate workflow
        return json_response.success(
            pdf_url=pdf_url,          # URL for PDF download/preview
            processo_id=processo_id,  # Database ID for prescription record
            operation='create',       # Operation type for frontend logic differentiation
            filename=filename         # Display filename for user feedback
        )
        
    except Exception as e:
        # Handle file I/O errors with detailed logging and graceful user feedback
        logger.error(f"Error in file operations: {str(e)}")
        return json_response.exception(e, context="operações de arquivo")



def _get_patient_context_data(request, setup):
    """
    Retrieves and prepares patient context data for existing patient prescription forms.
    
    Business Context:
    - Handles patient data versioning system that maintains privacy between different doctors
    - Each doctor sees only their own version of patient data, preventing data leakage
    - Combines master patient record with doctor-specific versioned data
    - Prepares data for form pre-population and conditional field display
    
    Data Privacy Architecture:
    - Master patient record: contains immutable data (ID, CPF, basic demographics)
    - Versioned patient data: doctor-specific patient information and medical history
    - Conditional fields: dynamic form behavior based on patient history and disease type
    
    Error Handling:
    - Session validation ensures patient ID exists and is accessible
    - Repository pattern abstracts data access and handles database errors
    - Graceful fallback to master record if versioning data unavailable
    
    Returns:
    - Dictionary with patient data ready for template context and form initialization
    - Includes both raw patient data and processed conditional field configurations
    """
    # Validate that patient ID exists in session - required for existing patient workflow
    # Patient ID is set in previous workflow step (patient search/selection)
    if "paciente_id" not in request.session:
        raise ValueError("ID do paciente não encontrado na sessão.")
    
    # Extract patient ID from session - guaranteed to be valid integer at this point
    paciente_id = request.session["paciente_id"]
    
    # Use repository pattern for data access - abstracts database operations and error handling
    # Repository ensures proper error handling and data consistency
    from ..repositories.patient_repository import PatientRepository
    patient_repo = PatientRepository()
    paciente = patient_repo.get_patient_by_id(paciente_id)
    
    # CRITICAL: Retrieve doctor-specific versioned patient data for data privacy
    # Each doctor maintains their own version of patient data to prevent information leakage
    # This ensures that Doctor A cannot see patient information collected by Doctor B
    user = request.user
    version = patient_repo.get_patient_version_for_user(paciente, user)
    
    if version:
        # Use versioned data as primary source - contains doctor-specific patient information
        # This is the most common scenario for existing patients with established medical history
        dados_paciente = model_to_dict(version)
        
        # Preserve critical master record fields that are never versioned
        # These fields are immutable and shared across all doctor versions
        dados_paciente['id'] = paciente.id                    # Database primary key
        dados_paciente['cpf_paciente'] = paciente.cpf_paciente # Brazilian CPF (tax ID)
        dados_paciente['usuarios'] = paciente.usuarios.all()  # Associated user accounts
    else:
        # NO FALLBACK TO MASTER RECORD - maintains privacy isolation
        # When doctor accesses patient for first time, start with blank form
        # Patient data will come from form submission and create new version
        dados_paciente = {
            'id': paciente.id,
            'cpf_paciente': paciente.cpf_paciente,  # Only share CPF (patient identifier)
            'usuarios': paciente.usuarios.all()     # Associated user accounts
            # All other fields intentionally blank - doctor must fill form
        }
    
    # Add prescription-specific context data using domain repository
    # Disease information and prescription metadata required for form display
    from ..repositories.domain_repository import DomainRepository
    domain_repo = DomainRepository()
    disease = domain_repo.get_disease_by_cid(setup.form.cid)
    
    # Enhance patient data with prescription-specific information
    dados_paciente["diagnostico"] = disease.nome              # Disease name for display
    dados_paciente["cid"] = setup.form.cid                    # CID-10 disease code
    dados_paciente["data_1"] = setup.specific.primeira_data   # First prescription date
    
    # Process conditional fields for dynamic form behavior
    # Some form fields are shown/hidden based on patient history and disease type
    # This is critical for medical forms where field relevance depends on clinical context
    from ..services.view_services import PrescriptionViewSetupService
    service = PrescriptionViewSetupService()
    campos_ajustados, _ = service.adjust_conditional_fields(dados_paciente)
    
    # Build final context dictionary for template rendering
    # Includes both raw patient object and processed field configurations
    context = {"paciente": paciente}  # Raw patient object for template access
    context.update(campos_ajustados)  # Processed fields for conditional display logic
    
    return context