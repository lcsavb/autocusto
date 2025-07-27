"""
Prescription Views - New prescription and editing functionality

This module contains views for prescription creation and editing with simplified control flow.
"""

import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.forms.models import model_to_dict
from pacientes.models import Paciente
from processos.models import Doenca
# Removed deprecated form imports - now using service methods
from processos.utils.url_utils import generate_protocol_link
from processos.services.view_services import PrescriptionViewSetupService
from processos.services.view_setup_models import SetupError
from processos.utils.pdf_json_response_helper import PDFJsonResponseHelper

logger = logging.getLogger(__name__)


@login_required
def edicao(request):
    """
    Handles editing of existing medical prescription processes with simplified control flow.
    
    Clean view that delegates setup logic to PrescriptionViewSetupService.
    Focuses only on HTTP concerns and coordination.
    """
    # Setup all view data using service
    setup_service = PrescriptionViewSetupService()
    setup = setup_service.setup_for_edit_prescription(request)
    
    # Handle setup errors with early return
    if isinstance(setup, SetupError):
        messages.error(request, setup.message)
        return redirect(setup.redirect_to)
    
    # Extract setup data
    usuario = setup.common.usuario
    medico = setup.common.medico
    escolhas = setup.common.escolhas
    medicamentos = setup.form.medicamentos
    ModeloFormulario = setup.form.ModeloFormulario
    processo = setup.specific.processo
    processo_id = setup.specific.processo_id

    # Handle POST request using new helper function
    if request.method == "POST":
        return _handle_prescription_edit_post(request, setup, ModeloFormulario, escolhas, medicamentos, processo_id)
    
    # Handle GET request - form initialization
    formulario = ModeloFormulario(escolhas, medicamentos, initial=setup.specific.dados_iniciais)
    
    # Set up template context using service methods
    setup_service_instance = PrescriptionViewSetupService()
    campos_condicionais = setup_service_instance.extract_conditional_fields(formulario)
    link_protocolo = generate_protocol_link(setup.form.cid)

    contexto = {
        "formulario": formulario,
        "processo": processo,
        "campos_condicionais": campos_condicionais,
        "link_protocolo": link_protocolo,
    }
    # Use service method for medication display classes
    display_service = PrescriptionViewSetupService()
    contexto.update(display_service.get_medication_display_classes(True, processo))

    return render(request, "processos/edicao.html", contexto)


@login_required
def cadastro(request):
    """
    Handles the registration of new medical prescription processes with simplified control flow.
    
    Clean view that delegates setup logic to PrescriptionViewSetupService.
    Focuses only on HTTP concerns and coordination.
    """
    # Setup all view data using service
    setup_service = PrescriptionViewSetupService()
    setup = setup_service.setup_for_new_prescription(request)
    
    # Handle setup errors with early return
    if isinstance(setup, SetupError):
        messages.error(request, setup.message)
        return redirect(setup.redirect_to)
    
    # Extract setup data
    usuario = setup.common.usuario
    medico = setup.common.medico
    escolhas = setup.common.escolhas
    paciente_existe = setup.specific.paciente_existe
    medicamentos = setup.form.medicamentos
    ModeloFormulario = setup.form.ModeloFormulario
    
    # Handle POST request
    if request.method == "POST":
        return _handle_prescription_create_post(request, setup, ModeloFormulario, escolhas, medicamentos, paciente_existe)
    
    # Handle GET request - template rendering (HTTP concern)
    try:
        # Validate doctor profile completeness
        validation_service = PrescriptionViewSetupService()
        profile_error = validation_service.validate_doctor_profile_completeness(medico, usuario)
        
        if profile_error:
            messages.info(request, profile_error.message)
            return redirect(profile_error.redirect_to)
        
        # Create form with initial data
        formulario = ModeloFormulario(escolhas, medicamentos, initial=setup.specific.dados_iniciais)
        
        # Setup context for template rendering using service methods
        setup_service_instance = PrescriptionViewSetupService()
        campos_condicionais = setup_service_instance.extract_conditional_fields(formulario)
        link_protocolo = generate_protocol_link(setup.form.cid)
        
        contexto = {
            "formulario": formulario,
            "paciente_existe": paciente_existe,
            "campos_condicionais": campos_condicionais,
            "link_protocolo": link_protocolo,
        }
        
        # Add patient data if exists
        if paciente_existe:
            contexto.update(_get_patient_context_data(request, setup))
        
        contexto.update(setup_service_instance.get_medication_display_classes(False))
        return render(request, "processos/cadastro.html", contexto)
        
    except Exception as e:
        messages.error(request, f"Erro ao carregar formulário de cadastro: {e}")
        return redirect("home")


def _handle_prescription_edit_post(request, setup, ModeloFormulario, escolhas, medicamentos, processo_id):
    """Handle POST request for prescription editing - HTTP concerns only."""
    from processos.services.prescription_services import PrescriptionService
    from processos.services.io_services import PDFFileService
    from processos.utils.pdf_json_response_helper import PDFJsonResponseHelper
    import os
    
    # Extract setup data
    usuario = setup.common.usuario
    medico = setup.common.medico
    json_response = PDFJsonResponseHelper()
    
    # Form validation (HTTP concern)
    try:
        formulario = ModeloFormulario(escolhas, medicamentos, request.POST)
        if not formulario.is_valid():
            return json_response.form_validation_failed(formulario.errors)
        
        dados_formulario = formulario.cleaned_data
        clinica = medico.clinicas.get(id=dados_formulario["clinicas"])
    except Exception as e:
        logger.error(f"Error in form processing: {str(e)}")
        return json_response.exception(e, context="validação do formulário")
    
    # Business logic (delegate to service)
    try:
        prescription_service = PrescriptionService()
        pdf_response, updated_processo_id = prescription_service.create_or_update_prescription(
            form_data=dados_formulario,
            user=usuario,
            medico=medico,
            clinica=clinica,
            patient_exists=True,
            process_id=processo_id
        )
        
        if not pdf_response or not updated_processo_id:
            return json_response.pdf_generation_failed()
            
    except Exception as e:
        logger.error(f"Error updating prescription: {str(e)}")
        return json_response.exception(e, context="atualização da prescrição")
    
    # File I/O (HTTP concern)
    try:
        file_service = PDFFileService()
        pdf_url = file_service.save_pdf_and_get_url(
            pdf_response, 
            dados_formulario.get('cpf_paciente', 'unknown'),
            dados_formulario.get('cid', 'unknown')
        )
        
        if not pdf_url:
            return json_response.pdf_save_failed()
        
        # Session management (HTTP concern)
        filename = os.path.basename(pdf_url.rstrip('/'))
        request.session["path_pdf_final"] = pdf_url
        request.session["processo_id"] = updated_processo_id
        
        logger.info(f"Prescription updated successfully: Process {updated_processo_id}")
        return json_response.success(
            pdf_url=pdf_url,
            processo_id=updated_processo_id,
            operation='update',
            filename=filename
        )
        
    except Exception as e:
        logger.error(f"Error in file operations: {str(e)}")
        return json_response.exception(e, context="operações de arquivo")


def _handle_prescription_create_post(request, setup, ModeloFormulario, escolhas, medicamentos, paciente_existe):
    """Handle POST request for prescription creation - HTTP concerns only."""
    from processos.services.prescription_services import PrescriptionService
    from processos.services.io_services import PDFFileService
    from processos.utils.pdf_json_response_helper import PDFJsonResponseHelper
    import os
    
    # Extract setup data
    usuario = setup.common.usuario
    medico = setup.common.medico
    json_response = PDFJsonResponseHelper()
    
    # Form validation (HTTP concern)
    try:
        formulario = ModeloFormulario(escolhas, medicamentos, request.POST)
        if not formulario.is_valid():
            return json_response.form_validation_failed(formulario.errors)
        
        dados_formulario = formulario.cleaned_data
        clinica = medico.clinicas.get(id=dados_formulario["clinicas"])
    except Exception as e:
        logger.error(f"Error in form processing: {str(e)}")
        return json_response.exception(e, context="validação do formulário")
    
    # Business logic (delegate to service)
    try:
        prescription_service = PrescriptionService()
        pdf_response, processo_id = prescription_service.create_or_update_prescription(
            form_data=dados_formulario,
            user=usuario,
            medico=medico,
            clinica=clinica,
            patient_exists=paciente_existe,
            process_id=None
        )
        
        if not pdf_response or not processo_id:
            return json_response.pdf_generation_failed()
            
    except Exception as e:
        logger.error(f"Error creating prescription: {str(e)}")
        return json_response.exception(e, context="criação da prescrição")
    
    # File I/O (HTTP concern)
    try:
        file_service = PDFFileService()
        pdf_url = file_service.save_pdf_and_get_url(
            pdf_response, 
            dados_formulario.get('cpf_paciente', 'unknown'),
            dados_formulario.get('cid', 'unknown')
        )
        
        if not pdf_url:
            return json_response.pdf_save_failed()
        
        # Session management (HTTP concern)
        filename = os.path.basename(pdf_url.rstrip('/'))
        request.session["processo_id"] = processo_id
        
        logger.info(f"Prescription created successfully: Process {processo_id}")
        return json_response.success(
            pdf_url=pdf_url,
            processo_id=processo_id,
            operation='create',
            filename=filename
        )
        
    except Exception as e:
        logger.error(f"Error in file operations: {str(e)}")
        return json_response.exception(e, context="operações de arquivo")



def _get_patient_context_data(request, setup):
    """Get patient context data for existing patient forms."""
    if "paciente_id" not in request.session:
        raise ValueError("ID do paciente não encontrado na sessão.")
    
    paciente_id = request.session["paciente_id"]
    # Use repository instead of direct database access
    from ..repositories.patient_repository import PatientRepository
    patient_repo = PatientRepository()
    paciente = patient_repo.get_patient_by_id(paciente_id)
    
    # Get user's versioned data using PatientRepository
    user = request.user
    version = patient_repo.get_patient_version_for_user(paciente, user)
    
    if version:
        # Use versioned data for conditional fields
        dados_paciente = model_to_dict(version)
        # Keep master record fields that aren't versioned
        dados_paciente['id'] = paciente.id
        dados_paciente['cpf_paciente'] = paciente.cpf_paciente
        dados_paciente['usuarios'] = paciente.usuarios.all()
    else:
        # Fallback to master record if no version found
        dados_paciente = model_to_dict(paciente)
    
    # Add prescription-specific data using repository
    from ..repositories.domain_repository import DomainRepository
    domain_repo = DomainRepository()
    disease = domain_repo.get_disease_by_cid(setup.form.cid)
    dados_paciente["diagnostico"] = disease.nome
    dados_paciente["cid"] = setup.form.cid
    dados_paciente["data_1"] = setup.specific.primeira_data
    
    # Get adjusted fields for conditional display using service method
    from ..services.view_services import PrescriptionViewSetupService
    service = PrescriptionViewSetupService()
    campos_ajustados, _ = service.adjust_conditional_fields(dados_paciente)
    
    context = {"paciente": paciente}
    context.update(campos_ajustados)
    return context