"""
Renewal Views - Quick Prescription Renewal Functionality

This module handles the "renovação rápida" (quick renewal) functionality for medical prescriptions
in the Brazilian healthcare system. Unlike new prescriptions that require full patient consultation
and medical assessment, renewals allow doctors to extend existing prescriptions for chronic conditions
or ongoing treatments with minimal intervention.

Key Business Context:
- Brazilian medical regulations allow prescription renewals for specific medication categories
- Renewals maintain the same medication, dosage, and treatment plan as the original prescription
- Only the validity dates are updated, reducing administrative burden on healthcare providers
- This supports continuity of care for patients with chronic conditions requiring long-term medication

Technical Architecture:
- Follows clean architecture with service delegation pattern
- Views handle only HTTP concerns (request/response, routing, error presentation)
- Business logic is delegated to specialized services (RenewalService, PDFFileService)
- Uses early return pattern for simplified control flow and better error handling
- Supports both traditional HTTP and AJAX requests for modern web UX

The renewal workflow differs from new prescriptions by:
1. Bypassing full medical assessment forms
2. Reusing existing patient and medication data
3. Only requiring new validity dates
4. Generating PDF with updated dates but same clinical content
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

# Logging setup for different aspects of the renewal process
logger = logging.getLogger(__name__)  # General application logging
pdf_logger = logging.getLogger('processos.pdf')  # PDF generation performance and status
audit_logger = logging.getLogger('processos.audit')  # Medical audit trail for compliance


@login_required
def renovacao_rapida(request):
    """
    Main entry point for prescription renewal functionality.
    
    This view implements the Brazilian healthcare quick renewal process ("renovação rápida"),
    which allows licensed medical professionals to extend existing prescriptions without
    requiring a full new consultation. This is particularly important for:
    
    - Chronic disease management (diabetes, hypertension, etc.)
    - Long-term psychiatric medications
    - Maintenance therapies that require continuous medication
    
    Security & Compliance:
    - Requires user authentication (@login_required)
    - All actions are logged for medical audit trails
    - Only authorized medical professionals can perform renewals
    
    HTTP Flow:
    - GET: Display renewal form with patient search and existing prescription data
    - POST: Process renewal request, validate dates, generate updated PDF prescription
    
    Args:
        request: Django HTTP request object containing user authentication and form data
        
    Returns:
        HttpResponse: Either rendered form (GET) or PDF generation result (POST)
    """
    
    if request.method == "GET":
        # Display the renewal form with patient search capabilities
        return _handle_renewal_get_request(request)
    
    # Process the renewal submission with form validation and PDF generation
    return _handle_renewal_post_request(request)


def _handle_renewal_get_request(request):
    try:
        # Extract patient search parameter - 'b' is short for 'busca' (search in Portuguese)
        # This allows direct linking to specific patient searches via URL
        busca = request.GET.get("b")
        
        # Store search term in session to maintain state across form submissions
        # This is crucial for renewal workflow as users often need to navigate back and forth
        request.session["busca"] = busca
        
        # Delegate to service layer for building consistent patient context
        # This service handles patient search, prescription filtering, and permission checks
        setup_service = PrescriptionViewSetupService()
        contexto = setup_service.build_patient_search_context(request.user, busca)
        
        # Render the renewal form template with populated patient data
        return render(request, "processos/renovacao_rapida.html", contexto)
        
    except Exception as e:
        # Log error with full stack trace for debugging
        logger.error(f"Error in renewal GET request: {e}", exc_info=True)
        
        # Show user-friendly error message and redirect to safe page
        messages.error(request, f"Erro ao carregar página: {str(e)}")
        return redirect("home")


def _handle_renewal_post_request(request):
    form = RenovacaoRapidaForm(request.POST)
    if not form.is_valid():
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # For AJAX requests, return JSON with form errors
            json_response = PDFJsonResponseHelper()
            return json_response.form_validation_failed(form.errors)
        else:
            # For traditional requests, add validation errors to Django messages
            _add_form_errors_to_messages(request, form)
            # Redirect back to form page to display errors
            return redirect("processos-renovacao-rapida")
    
    # Step 2: Extract validated form data for processing
    usuario = request.user  # Current authenticated medical professional
    processo_id = form.cleaned_data["processo_id"]  # Original prescription identifier
    nova_data = form.cleaned_data["data_1"]  # New prescription validity start date
    
    # Step 3: Route to appropriate renewal handler based on submission mode
    if request.POST.get("edicao"):
        # Edit mode: User wants to modify prescription details before renewal
        # This redirects to full prescription editing interface
        return _handle_renewal_edit_mode(request, processo_id, nova_data)
    
    # Default mode: Direct PDF generation with minimal changes
    # This is the most common renewal workflow for straightforward renewals
    return _handle_renewal_pdf_generation(request, processo_id, nova_data, usuario)


def _handle_renewal_edit_mode(request, processo_id, nova_data):
    setup_service = PrescriptionViewSetupService()
    result = setup_service.setup_process_for_renewal_editing(processo_id, request.user, request, nova_data)
    
    # Check for setup errors using type-safe error handling pattern
    if isinstance(result, SetupError):
        # Display error message to user through Django messages
        messages.error(request, result.message)
        # Redirect to appropriate error page (may be renewal form or general error page)
        return redirect(result.redirect_to)
    
    # Success case: redirect to the prescription editing interface
    # The service provides the specific URL for the editing page with proper context
    return redirect(result.specific['redirect_to'])


def _handle_renewal_pdf_generation(request, processo_id, nova_data, usuario):
    json_response = PDFJsonResponseHelper()
    
    # Phase 1: Generate the renewal PDF document
    try:
        # Start performance timing for monitoring PDF generation speed
        start_time = time.time()
        
        # Log renewal initiation for audit trail and debugging
        pdf_logger.info(f"Starting PDF renewal generation for processo {processo_id}")
        audit_logger.info(f"User {usuario.email} initiated renewal for processo {processo_id}")
        
        # Delegate to business service for PDF generation
        # RenewalService handles prescription data loading, date updates, and PDF creation
        renewal_service = RenewalService()
        pdf_response = renewal_service.process_renewal(nova_data, int(processo_id), usuario)
        
        # Log completion time for performance monitoring
        total_time = time.time() - start_time
        pdf_logger.info(f"PDF generation completed in {total_time:.3f}s")
        
    except Exception as e:
        # Log detailed error for debugging while providing user-friendly message
        logger.error(f"Error generating renewal PDF: {e}", exc_info=True)
        return _handle_renewal_error(request, json_response, f"Erro na geração: {str(e)}")
    
    # Early return pattern: Check if PDF generation succeeded
    if not pdf_response:
        logger.error("Failed to generate PDF for renewal")
        pdf_logger.error("PDF generation failed for renewal")
        return _handle_renewal_error(request, json_response, "Falha ao gerar PDF")
    
    # Phase 2: Save PDF file to filesystem and generate access URL
    try:
        # Generate renewal data for file naming and metadata
        # This includes patient CPF and medical condition code for unique file identification
        renewal_service = RenewalService()
        dados_renovacao = renewal_service.generate_renewal_data(nova_data, int(processo_id), usuario)
        
        # Save PDF file and get public URL for access
        # File naming uses patient CPF and CID to ensure uniqueness and audit compliance
        file_service = PDFFileService()
        pdf_url = file_service.save_pdf_and_get_url(
            pdf_response,
            dados_renovacao.get('cpf_paciente', 'unknown'),  # Patient Brazilian tax ID
            dados_renovacao.get('cid', 'unknown')  # Medical condition code (CID-10)
        )
    except Exception as e:
        # Log file saving errors separately from PDF generation errors
        logger.error(f"Error saving renewal PDF: {e}", exc_info=True)
        return _handle_renewal_error(request, json_response, f"Erro ao salvar PDF: {str(e)}")
    
    # Early return pattern: Check if file saving succeeded
    if not pdf_url:
        logger.error("PDF saving failed for renewal")
        return _handle_renewal_error(request, json_response, "Falha ao salvar PDF")
    
    # Success: Return appropriate response based on request type (AJAX vs traditional)
    return _handle_renewal_success(request, json_response, pdf_url, processo_id)


def _handle_renewal_success(request, json_response, pdf_url, processo_id):
    filename = os.path.basename(pdf_url.rstrip('/'))
    
    # Check for AJAX request using standard HTTP header
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Modern web interface: Return structured JSON response
        # This allows JavaScript to handle PDF display, notifications, and UI updates
        return json_response.success(
            pdf_url=pdf_url,  # Full URL for accessing the generated PDF
            processo_id=processo_id,  # Original prescription ID for tracking
            operation='renew',  # Operation type for client-side routing
            filename=filename  # Extracted filename for proper download naming
        )
    else:
        # Traditional HTTP interface: Use Django messages and redirect
        # This provides fallback support for non-JavaScript scenarios
        messages.success(request, "Renovação processada com sucesso! PDF gerado.")
        return redirect(pdf_url)  # Direct redirect to PDF for immediate viewing


def _handle_renewal_error(request, json_response, error_message):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # AJAX error response: Return standardized JSON error
        # Uses generic error message for security (doesn't expose internal details)
        return json_response.pdf_generation_failed()
    else:
        # Traditional HTTP error response: Show specific error and re-render form
        # Display specific error message through Django messages framework
        messages.error(request, error_message)
        
        # Re-render renewal form with preserved context and user input
        # This maintains user's search state and form data for better UX
        return _render_renewal_form_with_context(request)


def _render_renewal_form_with_context(request):
    busca = request.session.get("busca", "")
    
    # Use same service as initial form rendering to ensure consistency
    # This builds patient search context with proper authorization and filtering
    setup_service = PrescriptionViewSetupService()
    contexto = setup_service.build_patient_search_context(request.user, busca)
    
    # Render the same template used for successful GET requests
    # This ensures consistent UI while displaying error messages through Django messages
    return render(request, "processos/renovacao_rapida.html", contexto)


def _add_form_errors_to_messages(request, form):
    for errors in form.errors.values():
        # Process each individual error message for the field
        for error in errors:
            # Add each error as a message for user display
            # Uses 'error' level for proper CSS styling and user attention
            messages.error(request, error)