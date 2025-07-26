"""
Renewal Views - Quick renewal functionality

This module contains views for prescription renewal with simplified control flow.
"""

import os
import time
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from processos.forms import RenovacaoRapidaForm
from processos.services.view_services import PrescriptionViewSetupService
from processos.services.view_setup_models import SetupError
from processos.services.prescription_services import RenewalService
from processos.services.io_services import PDFFileService
from processos.utils.pdf_json_response_helper import PDFJsonResponseHelper

logger = logging.getLogger(__name__)
pdf_logger = logging.getLogger('processos.pdf')
audit_logger = logging.getLogger('processos.audit')


@login_required
def renovacao_rapida(request):
    """Handles the quick renewal process with simplified control flow."""
    
    if request.method == "GET":
        return _handle_renewal_get_request(request)
    
    # Handle POST request
    return _handle_renewal_post_request(request)


def _handle_renewal_get_request(request):
    """Handle GET request for renewal page."""
    try:
        busca = request.GET.get("b")
        request.session["busca"] = busca
        
        # Use service to build standard patient context
        setup_service = PrescriptionViewSetupService()
        contexto = setup_service.build_patient_search_context(request.user, busca)
        return render(request, "processos/renovacao_rapida.html", contexto)
        
    except Exception as e:
        logger.error(f"Error in renewal GET request: {e}", exc_info=True)
        messages.error(request, f"Erro ao carregar página: {str(e)}")
        return redirect("home")


def _handle_renewal_post_request(request):
    """Handle POST request for renewal processing with early returns."""
    
    # Validate form
    form = RenovacaoRapidaForm(request.POST)
    if not form.is_valid():
        _add_form_errors_to_messages(request, form)
        return redirect("processos-renovacao-rapida")
    
    # Extract validated data
    usuario = request.user
    processo_id = form.cleaned_data["processo_id"]
    nova_data = form.cleaned_data["data_1"]
    
    # Handle edit mode
    if request.POST.get("edicao"):
        return _handle_renewal_edit_mode(request, processo_id, nova_data)
    
    # Handle PDF generation mode
    return _handle_renewal_pdf_generation(request, processo_id, nova_data, usuario)


def _handle_renewal_edit_mode(request, processo_id, nova_data):
    """Handle renewal edit mode with simplified flow."""
    setup_service = PrescriptionViewSetupService()
    result = setup_service.setup_process_for_renewal_editing(processo_id, request.user, request, nova_data)
    
    if isinstance(result, SetupError):
        messages.error(request, result.message)
        return redirect(result.redirect_to)
    
    # Success - redirect to editing
    return redirect(result.specific['redirect_to'])


def _handle_renewal_pdf_generation(request, processo_id, nova_data, usuario):
    """Handle PDF generation for renewal with simplified flow."""
    json_response = PDFJsonResponseHelper()
    
    # Step 1: Generate PDF
    try:
        start_time = time.time()
        pdf_logger.info(f"Starting PDF renewal generation for processo {processo_id}")
        audit_logger.info(f"User {usuario.email} initiated renewal for processo {processo_id}")
        
        renewal_service = RenewalService()
        pdf_response = renewal_service.process_renewal(nova_data, int(processo_id), usuario)
        
        total_time = time.time() - start_time
        pdf_logger.info(f"PDF generation completed in {total_time:.3f}s")
        
    except Exception as e:
        logger.error(f"Error generating renewal PDF: {e}", exc_info=True)
        return _handle_renewal_error(request, json_response, f"Erro na geração: {str(e)}")
    
    # Early return if PDF generation failed
    if not pdf_response:
        logger.error("Failed to generate PDF for renewal")
        pdf_logger.error("PDF generation failed for renewal")
        return _handle_renewal_error(request, json_response, "Falha ao gerar PDF")
    
    # Step 2: Save PDF file
    try:
        renewal_service = RenewalService()
        dados_renovacao = renewal_service.generate_renewal_data(nova_data, int(processo_id), usuario)
        
        file_service = PDFFileService()
        pdf_url = file_service.save_pdf_and_get_url(
            pdf_response,
            dados_renovacao.get('cpf_paciente', 'unknown'),
            dados_renovacao.get('cid', 'unknown')
        )
    except Exception as e:
        logger.error(f"Error saving renewal PDF: {e}", exc_info=True)
        return _handle_renewal_error(request, json_response, f"Erro ao salvar PDF: {str(e)}")
    
    # Early return if PDF saving failed
    if not pdf_url:
        logger.error("PDF saving failed for renewal")
        return _handle_renewal_error(request, json_response, "Falha ao salvar PDF")
    
    # Step 3: Return success response
    return _handle_renewal_success(request, json_response, pdf_url, processo_id)


def _handle_renewal_success(request, json_response, pdf_url, processo_id):
    """Handle successful renewal response."""
    filename = os.path.basename(pdf_url.rstrip('/'))
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # AJAX response
        return json_response.success(
            pdf_url=pdf_url,
            processo_id=processo_id,
            operation='renew',
            filename=filename
        )
    else:
        # Traditional response
        messages.success(request, "Renovação processada com sucesso! PDF gerado.")
        return redirect(pdf_url)


def _handle_renewal_error(request, json_response, error_message):
    """Handle renewal error responses."""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # AJAX error response
        return json_response.pdf_generation_failed()
    else:
        # Traditional error response
        messages.error(request, error_message)
        return _render_renewal_form_with_context(request)


def _render_renewal_form_with_context(request):
    """Render renewal form with proper context after error."""
    busca = request.session.get("busca", "")
    setup_service = PrescriptionViewSetupService()
    contexto = setup_service.build_patient_search_context(request.user, busca)
    return render(request, "processos/renovacao_rapida.html", contexto)


def _add_form_errors_to_messages(request, form):
    """Add form validation errors to Django messages."""
    for field, errors in form.errors.items():
        for error in errors:
            messages.error(request, error)