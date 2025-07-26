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
from processos.forms import (
    extrair_campos_condicionais,
    ajustar_campos_condicionais,
    mostrar_med,
)
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
    
    # Set up template context
    campos_condicionais = extrair_campos_condicionais(formulario)
    link_protocolo = generate_protocol_link(setup.form.cid)

    contexto = {
        "formulario": formulario,
        "processo": processo,
        "campos_condicionais": campos_condicionais,
        "link_protocolo": link_protocolo,
    }
    contexto.update(mostrar_med(True, processo))

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
    
    # Handle GET request
    return _handle_prescription_create_get(request, setup, ModeloFormulario, escolhas, medicamentos, paciente_existe, medico, usuario)


def _handle_prescription_edit_post(request, setup, ModeloFormulario, escolhas, medicamentos, processo_id):
    """Handle POST request for prescription editing using workflow service."""
    from processos.services.prescription_services import PrescriptionService
    from processos.services.io_services import PDFFileService
    from processos.utils.pdf_json_response_helper import PDFJsonResponseHelper
    import os
    
    # Extract setup data
    usuario = setup.common.usuario
    medico = setup.common.medico
    
    # Initialize response helper
    json_response = PDFJsonResponseHelper()
    
    # Create and validate form
    try:
        formulario = ModeloFormulario(escolhas, medicamentos, request.POST)
    except Exception as e:
        logger.error(f"Error creating form: {str(e)}")
        return json_response.exception(e, context="criação do formulário")
    
    # Early return for invalid form
    if not formulario.is_valid():
        logger.error(f"Form validation failed: {formulario.errors}")
        return json_response.form_validation_failed(formulario.errors)
    
    # Extract validated data
    dados_formulario = formulario.cleaned_data
    id_clin = dados_formulario["clinicas"]
    
    try:
        clinica = medico.clinicas.get(id=id_clin)
    except Exception as e:
        logger.error(f"Error getting clinic {id_clin}: {str(e)}")
        return json_response.exception(e, context="busca da clínica")
    
    # Process prescription update
    try:
        prescription_service = PrescriptionService()
        pdf_response, updated_processo_id = prescription_service.create_or_update_prescription(
            form_data=dados_formulario,
            user=usuario,
            medico=medico,
            clinica=clinica,
            patient_exists=True,  # For edit, patient always exists
            process_id=processo_id  # Update existing prescription
        )
    except Exception as e:
        logger.error(f"Error updating prescription: {str(e)}")
        return json_response.exception(e, context="atualização da prescrição")
    
    # Early return if prescription service failed
    if not pdf_response or not updated_processo_id:
        logger.error("Prescription service returned null response")
        return json_response.pdf_generation_failed()
    
    # Save PDF file
    try:
        file_service = PDFFileService()
        pdf_url = file_service.save_pdf_and_get_url(
            pdf_response, 
            dados_formulario.get('cpf_paciente', 'unknown'),
            dados_formulario.get('cid', 'unknown')
        )
    except Exception as e:
        logger.error(f"Error saving PDF: {str(e)}")
        return json_response.exception(e, context="salvamento do PDF")
    
    # Early return if PDF saving failed
    if not pdf_url:
        logger.error("PDF file service returned null URL")
        return json_response.pdf_save_failed()
    
    # Success - update session and return response
    try:
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
        logger.error(f"Error finalizing response: {str(e)}")
        return json_response.exception(e, context="finalização")


def _handle_prescription_create_post(request, setup, ModeloFormulario, escolhas, medicamentos, paciente_existe):
    """Handle POST request for prescription creation using workflow service."""
    from processos.services.prescription_services import PrescriptionService
    from processos.services.io_services import PDFFileService
    from processos.utils.pdf_json_response_helper import PDFJsonResponseHelper
    import os
    
    # Extract setup data
    usuario = setup.common.usuario
    medico = setup.common.medico
    
    # Initialize response helper
    json_response = PDFJsonResponseHelper()
    
    # Create and validate form
    try:
        formulario = ModeloFormulario(escolhas, medicamentos, request.POST)
    except Exception as e:
        logger.error(f"Error creating form: {str(e)}")
        return json_response.exception(e, context="criação do formulário")
    
    # Early return for invalid form
    if not formulario.is_valid():
        logger.error(f"Form validation failed: {formulario.errors}")
        return json_response.form_validation_failed(formulario.errors)
    
    # Extract validated data
    dados_formulario = formulario.cleaned_data
    id_clin = dados_formulario["clinicas"]
    
    try:
        clinica = medico.clinicas.get(id=id_clin)
    except Exception as e:
        logger.error(f"Error getting clinic {id_clin}: {str(e)}")
        return json_response.exception(e, context="busca da clínica")
    
    # Process prescription creation
    try:
        prescription_service = PrescriptionService()
        pdf_response, processo_id = prescription_service.create_or_update_prescription(
            form_data=dados_formulario,
            user=usuario,
            medico=medico,
            clinica=clinica,
            patient_exists=paciente_existe,
            process_id=None  # New prescription
        )
    except Exception as e:
        logger.error(f"Error creating prescription: {str(e)}")
        return json_response.exception(e, context="criação da prescrição")
    
    # Early return if prescription service failed
    if not pdf_response or not processo_id:
        logger.error("Prescription service returned null response")
        return json_response.pdf_generation_failed()
    
    # Save PDF file
    try:
        file_service = PDFFileService()
        pdf_url = file_service.save_pdf_and_get_url(
            pdf_response, 
            dados_formulario.get('cpf_paciente', 'unknown'),
            dados_formulario.get('cid', 'unknown')
        )
    except Exception as e:
        logger.error(f"Error saving PDF: {str(e)}")
        return json_response.exception(e, context="salvamento do PDF")
    
    # Early return if PDF saving failed
    if not pdf_url:
        logger.error("PDF file service returned null URL")
        return json_response.pdf_save_failed()
    
    # Success - update session and return response
    try:
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
        logger.error(f"Error finalizing response: {str(e)}")
        return json_response.exception(e, context="finalização")


def _handle_prescription_create_get(request, setup, ModeloFormulario, escolhas, medicamentos, paciente_existe, medico, usuario):
    """Handle GET request for prescription creation form."""
    
    # Validate doctor profile completeness
    validation_service = PrescriptionViewSetupService()
    profile_error = validation_service.validate_doctor_profile_completeness(medico, usuario)
    
    if profile_error:
        messages.info(request, profile_error.message)
        return redirect(profile_error.redirect_to)
    
    # Create form with initial data
    try:
        formulario = ModeloFormulario(escolhas, medicamentos, initial=setup.specific.dados_iniciais)
    except Exception as e:
        messages.error(request, f"Erro ao carregar formulário de cadastro: {e}")
        return redirect("home")
    
    # Setup context for template rendering
    try:
        campos_condicionais = extrair_campos_condicionais(formulario)
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
        
        contexto.update(mostrar_med(False))
        return render(request, "processos/cadastro.html", contexto)
        
    except Exception as e:
        messages.error(request, f"Erro ao carregar formulário de cadastro: {e}")
        return redirect("home")


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
    
    # Get adjusted fields for conditional display
    campos_ajustados, _ = ajustar_campos_condicionais(dados_paciente)
    
    context = {"paciente": paciente}
    context.update(campos_ajustados)
    return context