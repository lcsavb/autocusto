from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponse, Http404
import json
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from django.db import IntegrityError
from django.core.cache import cache
from datetime import date
import logging
import traceback
import os
import mimetypes
import secrets
import time

logger = logging.getLogger(__name__)
pdf_logger = logging.getLogger('processos.pdf')
audit_logger = logging.getLogger('processos.audit')
from medicos.seletor import medico as seletor_medico
from pacientes.models import Paciente
from processos.models import Processo, Doenca
from analytics.models import PDFGenerationLog
from .forms import (
    mostrar_med,
    ajustar_campos_condicionais,
    extrair_campos_condicionais,
    fabricar_formulario,
)
from .helpers import (
    cria_dict_renovação,
    gerar_dados_renovacao,
    vincula_dados_emissor,
    transfere_dados_gerador,
    listar_med,
    gera_med_dosagem,
    resgatar_prescricao,
    gerar_lista_meds_ids,
    gerar_link_protocolo,
)


# English: _get_initial_data
def _get_initial_data(request, paciente_existe, primeira_data, cid):
    """
    Constructs initial form data based on patient existence and session context.
    
    This helper function handles two distinct scenarios in Brazilian medical prescription workflow:
    1. Existing patient: Pre-populate form with patient data from database
    2. New patient: Initialize form with minimal data from session (CPF + disease info)
    
    The function bridges the gap between session-based workflow state and form initialization,
    ensuring data consistency across the multi-step prescription process.

    Critique:
    - The function raises a generic `KeyError` if session data is missing.
      It would be better to raise a more specific custom exception to allow for
      more granular error handling.
    
    Args:
        request: HTTP request containing session data
        # English: patient_exists
        paciente_existe (bool): Whether patient exists in doctor's database
        # English: first_date
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
        
        # English: patient_id
        paciente_id = request.session["paciente_id"]
        # English: patient
        paciente = Paciente.objects.get(id=paciente_id)
        
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
        # English: patient_data
        dados_paciente["diagnostico"] = Doenca.objects.get(cid=cid).nome
        # English: patient_data
        dados_paciente["cid"] = cid
        # English: patient_data
        dados_paciente["data_1"] = primeira_data
        
        return dados_paciente
    else:
        # New patient - minimal form initialization with session data
        if "cpf_paciente" not in request.session:
            raise KeyError("CPF do paciente não encontrado na sessão.")
        
        # Return minimal data structure for new patient form
        return {
            "cpf_paciente": request.session["cpf_paciente"],
            "data_1": primeira_data,
            "cid": cid,
            "diagnostico": Doenca.objects.get(cid=cid).nome,
        }


# search processes
@login_required
def busca_processos(request):
    """Searches for processes associated with the logged-in user.

    If the request is a GET, it displays a search form. If it's a POST, it
    searches for the specified process and, if found, redirects to the
    edition page.

    Args:
        request: The HTTP request.

    Returns:
        A rendered HTML page or a redirect.
    """
    if request.method == "GET":
        # English: user
        usuario = request.user
        # English: user_patients
        pacientes_usuario = usuario.pacientes.all()

        # English: context
        contexto = {"pacientes_usuario": pacientes_usuario, "usuario": usuario}
        return render(request, "processos/busca.html", contexto)
    else:
        # English: process_id
        processo_id = request.POST.get("processo_id")
        # Verify user owns this process
        try:
            # English: process
            processo = Processo.objects.get(id=processo_id, usuario=request.user)
            request.session["processo_id"] = processo_id
            request.session["cid"] = processo.doenca.cid
            messages.success(request, f"Processo selecionado: {processo.doenca.nome}")
            return redirect("processos-edicao")
        except Processo.DoesNotExist:
            messages.error(request, "Processo não encontrado ou você não tem permissão para acessá-lo.")
            return redirect("processos-busca")


# edition
@login_required
def edicao(request):
    """
    Handles editing of existing medical prescription processes.
    
    Clean view that delegates setup logic to PrescriptionViewSetupService.
    Focuses only on HTTP concerns and coordination.
    """
    # Setup all view data using service
    from processos.view_services import PrescriptionViewSetupService
    
    setup_service = PrescriptionViewSetupService()
    setup = setup_service.setup_for_edit_prescription(request)
    
    # Handle setup errors
    if not setup.success:
        messages.error(request, setup.error_message)
        return redirect(setup.error_redirect)
    
    # Extract setup data
    usuario = setup.usuario
    medico = setup.medico
    escolhas = setup.escolhas
    medicamentos = setup.medicamentos
    ModeloFormulario = setup.ModeloFormulario
    processo = setup.processo
    processo_id = setup.processo_id

    if request.method == "POST":
        logger.info("Processing POST request")
        # DEBUG: Print all field names received in POST request
        logger.info("=== DEBUG: POST Request Fields ===")
        for field_name, field_value in request.POST.items():
            logger.info(f"Field: {field_name} = {field_value}")
        logger.info("=== END DEBUG ===")

        # Since the template ALWAYS sends AJAX requests, we ALWAYS return JSON
        try:
            formulario = ModeloFormulario(escolhas, medicamentos, request.POST)
            logger.info(f"Formulario created successfully")

            if formulario.is_valid():
                logger.info("Formulario is valid, processing data")
                dados_formulario = formulario.cleaned_data
                logger.info(f"Dados formulario keys: {list(dados_formulario.keys())}")
                id_clin = dados_formulario["clinicas"]
                logger.info(f"Clinica ID selected: {id_clin}")
                clinica = medico.clinicas.get(id=id_clin)
                logger.info(f"Clinica found: {clinica}")
                try:
                    # Use new PrescriptionService for clean business logic
                    from processos.prescription_services import PrescriptionService
                    
                    # Use service to handle complete prescription update workflow
                    prescription_service = PrescriptionService()
                    pdf_response, updated_processo_id = prescription_service.create_or_update_prescription(
                        form_data=dados_formulario,
                        user=usuario,
                        medico=medico,
                        clinica=clinica,
                        patient_exists=True,  # For edit, patient always exists
                        process_id=processo_id  # Update existing prescription
                    )

                    if pdf_response and updated_processo_id:
                        # View layer handles file I/O operations
                        pdf_url = _save_pdf_for_serving(pdf_response, dados_formulario)
                        
                        if pdf_url:
                            # Extract filename from URL path for response
                            import os
                            filename = os.path.basename(pdf_url.rstrip('/'))
                            
                            request.session["path_pdf_final"] = pdf_url
                            request.session["processo_id"] = updated_processo_id
                            logger.info(f"Prescription updated successfully: Process {updated_processo_id}")
                            
                            return JsonResponse({
                                'success': True,
                                'pdf_url': pdf_url,
                                'processo_id': updated_processo_id,
                                'message': 'Processo atualizado com sucesso! PDF gerado.',
                                'filename': filename
                            })
                        else:
                            error_msg = 'Falha ao salvar PDF. Verifique se todos os arquivos necessários estão disponíveis.'
                            logger.error(f"PDF saving failed for user {usuario.email}")
                            
                            return JsonResponse({
                                'success': False,
                                'error': error_msg
                            })
                    else:
                        logger.error("Failed to update prescription or generate PDF")
                        return JsonResponse({
                            'success': False,
                            'error': 'Falha ao gerar PDF. Verifique se todos os arquivos necessários estão disponíveis.'
                        })
                except Exception as e:
                    logger.error(f"Error in form processing: {str(e)}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    return JsonResponse({
                        'success': False,
                        'error': f'Erro no processamento dos dados: {str(e)}'
                    })
            else:
                logger.error(f"Formulario validation failed: {formulario.errors}")
                return JsonResponse({
                    'success': False,
                    'error': 'Erro de validação do formulário.',
                    'form_errors': formulario.errors
                })
        except Exception as e:
            logger.error(f"Error in POST processing: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return JsonResponse({
                'success': False,
                'error': f'Erro no processamento: {str(e)}'
            })

    else:
        # GET request - use setup data for form initialization
        formulario = ModeloFormulario(escolhas, medicamentos, initial=setup.dados_iniciais)
    
    # Set up variables needed for template rendering (for both GET and POST with validation errors)
    # English: conditional_fields
    campos_condicionais = extrair_campos_condicionais(formulario)
    # English: protocol_link
    link_protocolo = gerar_link_protocolo(setup.cid)

    # English: context
    contexto = {
        "formulario": formulario,
        "processo": processo,
        "campos_condicionais": campos_condicionais,
        "link_protocolo": link_protocolo,
    }
    contexto.update(mostrar_med(True, processo))

    return render(request, "processos/edicao.html", contexto)


# quick renewal
@login_required
def renovacao_rapida(request):
    """Handles the quick renewal process.

    If the request is a GET, it displays a search form for patients. If it's a
    POST, it either redirects to the edition page or generates a new PDF for
    the renewal.

    Critique:
    - The function has a lot of debugging prints, which should be removed
      in a production environment. Using Python's `logging` module would be
      a better way to handle debugging information.
    - The error handling is very broad. It catches any exception and returns
      a generic error message. It would be better to catch specific exceptions
      and log them properly to make debugging easier.

    Args:
        request: The HTTP request.

    Returns:
        A rendered HTML page, a redirect, or a JSON response.
    """
    if request.method == "GET":
        try:
            print(f"DEBUG: GET request to renovacao_rapida")
            # English: search
            busca = request.GET.get("b")
            print(f"DEBUG: busca parameter = '{busca}'")
            
            # English: user
            usuario = request.user
            print(f"DEBUG: usuario = {usuario}")
            
            request.session["busca"] = busca
            
            # English: user_patients
            pacientes_usuario = usuario.pacientes.all()
            print(f"DEBUG: pacientes_usuario count = {pacientes_usuario.count()}")
            
            if busca:
                # Use versioned patient search
                from pacientes.models import Paciente
                patient_results = Paciente.get_patients_for_user_search(usuario, busca)
                busca_pacientes = [patient for patient, version in patient_results]
            else:
                # Empty list if no search
                busca_pacientes = []
            
            print(f"DEBUG: busca_pacientes count = {len(busca_pacientes)}")

            # English: context
            contexto = {"busca_pacientes": busca_pacientes, "usuario": usuario}
            print(f"DEBUG: About to render template")
            return render(request, "processos/renovacao_rapida.html", contexto)
            
        except Exception as e:
            print(f"ERROR: Exception in renovacao_rapida GET: {e}")
            print(f"ERROR: Exception type: {type(e)}")
            import traceback
            print(f"ERROR: Traceback: {traceback.format_exc()}")
            raise

    else:
        # English: user
        usuario = request.user
        # English: process_id
        processo_id = request.POST.get("processo_id")
        # English: new_date
        nova_data = request.POST.get("data_1")

        # Validate required fields
        print(f"[DEBUG] Renovacao validation - processo_id: '{processo_id}', nova_data: '{nova_data}'")
        validation_errors = False
        
        if not processo_id:
            print("[DEBUG] Adding error message: Selecione um processo para renovar")
            messages.error(request, "Selecione um processo para renovar")
            validation_errors = True
            
        if not nova_data or nova_data.strip() == "":
            print("[DEBUG] Adding error message: Data é obrigatória")
            messages.error(request, "Data é obrigatória")
            validation_errors = True
        
        # If there are validation errors, redirect back to the form
        if validation_errors:
            print("[DEBUG] Validation errors found, redirecting back to form")
            return redirect("processos-renovacao-rapida")

        # Check if user wants to edit the process
        if request.POST.get("edicao"):
            request.session["processo_id"] = processo_id
            request.session["cid"] = Processo.objects.get(id=processo_id).doenca.cid
            request.session["data1"] = nova_data
            return redirect("processos-edicao")
        
        # Generate PDF for renewal
        try:
            import time
            start_time = time.time()
            pdf_logger.info(f"Starting PDF renewal generation for processo {processo_id}")
            audit_logger.info(f"User {request.user.email} initiated renewal for processo {processo_id}")
            
            # Use new RenewalService for clean business logic
            from processos.prescription_services import RenewalService
            
            renewal_service = RenewalService()
            pdf_response = renewal_service.process_renewal(nova_data, int(processo_id), usuario)
            
            total_time = time.time() - start_time
            pdf_logger.info(f"PDF generation completed in {total_time:.3f}s")
            
            if pdf_response:
                # View layer handles file I/O operations - need to generate data for filename
                from processos.helpers import gerar_dados_renovacao
                dados_renovacao = gerar_dados_renovacao(nova_data, int(processo_id), usuario)
                pdf_url = _save_pdf_for_serving(pdf_response, dados_renovacao)
                
                if pdf_url:
                    # Extract filename from URL path
                    import os
                    filename = os.path.basename(pdf_url.rstrip('/'))
                    
                    # Check if this is an AJAX request
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        # Return JSON response for AJAX
                        return JsonResponse({
                            'success': True,
                            'pdf_url': pdf_url,
                            'processo_id': processo_id,
                            'message': 'Renovação processada com sucesso! PDF gerado.',
                            'filename': filename
                        })
                    else:
                        # Traditional redirect for non-AJAX requests
                        messages.success(request, "Renovação processada com sucesso! PDF gerado.")
                        return redirect(pdf_url)
                else:
                    error_msg = 'Falha ao salvar PDF de renovação.'
                    logger.error(f"PDF saving failed for renewal")
                    
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'error': error_msg
                        })
                    else:
                        messages.error(request, error_msg)
            else:
                logger.error("Failed to generate PDF for renewal")
                pdf_logger.error("PDF generation failed for renewal")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': 'Falha ao gerar PDF. Verifique os logs do sistema.'
                    })
                else:
                    messages.error(request, "Falha ao gerar PDF. Verifique os logs do sistema.")
        except Exception as e:
            logger.error(f"Exception in renovacao_rapida: {e}", exc_info=True)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': f'Erro interno: {str(e)}'
                })
            else:
                messages.error(request, f"Erro interno: {str(e)}")
        
        # On error, recreate the GET context and render the form again (non-AJAX only)
        # English: search
        busca = request.session.get("busca", "")
        # English: user
        usuario = request.user
        # English: user_patients
        pacientes_usuario = usuario.pacientes.all()
        
        # Use versioned patient search if busca exists
        if busca:
            from pacientes.models import Paciente
            patient_results = Paciente.get_patients_for_user_search(usuario, busca)
            # English: search_patients  
            busca_pacientes = [patient for patient, version in patient_results]
        else:
            # English: search_patients
            busca_pacientes = []
            
        # English: context
        contexto = {"busca_pacientes": busca_pacientes, "usuario": usuario}
        return render(request, "processos/renovacao_rapida.html", contexto)


# registration
@login_required
def cadastro(request):
    """
    Handles the registration of new medical prescription processes.
    
    Clean view that delegates setup logic to PrescriptionViewSetupService.
    Focuses only on HTTP concerns and coordination.
    """
    print(f"DEBUG CADASTRO: ============= CADASTRO VIEW CALLED =============")
    print(f"DEBUG CADASTRO: User: {request.user}")
    print(f"DEBUG CADASTRO: Request method: {request.method}")
    print(f"DEBUG CADASTRO: Request path: {request.path}")
    print(f"DEBUG CADASTRO: Session keys: {list(request.session.keys())}")
    
    # Setup all view data using service
    from processos.view_services import PrescriptionViewSetupService
    
    print(f"DEBUG CADASTRO: About to call setup service")
    setup_service = PrescriptionViewSetupService()
    setup = setup_service.setup_for_new_prescription(request)
    
    print(f"DEBUG CADASTRO: Setup completed")
    print(f"DEBUG CADASTRO: Setup success: {setup.success}")
    print(f"DEBUG CADASTRO: Setup error_redirect: {setup.error_redirect}")
    print(f"DEBUG CADASTRO: Setup error_message: {setup.error_message}")
    
    # Handle setup errors
    if not setup.success:
        print(f"DEBUG CADASTRO: Setup failed, redirecting to: {setup.error_redirect}")
        messages.error(request, setup.error_message)
        return redirect(setup.error_redirect)
    
    # Extract setup data
    usuario = setup.usuario
    medico = setup.medico
    escolhas = setup.escolhas
    paciente_existe = setup.paciente_existe
    medicamentos = setup.medicamentos
    ModeloFormulario = setup.ModeloFormulario
    
    print(f"DEBUG CADASTRO: Extracted data - usuario: {usuario}, medico: {medico}")
    if medico:
        print(f"DEBUG CADASTRO: medico.crm_medico: {repr(medico.crm_medico)}")
        print(f"DEBUG CADASTRO: medico.cns_medico: {repr(medico.cns_medico)}")

    if request.method == "POST":
        # Since the template ALWAYS sends AJAX requests, we ALWAYS return JSON
        try:
            # English: form
            formulario = ModeloFormulario(escolhas, medicamentos, request.POST)

            if formulario.is_valid():
                # Use new PrescriptionService for clean business logic
                from processos.prescription_services import PrescriptionService
                
                # English: form_data
                dados_formulario = formulario.cleaned_data
                # English: clinic_id
                id_clin = dados_formulario["clinicas"]
                # English: clinic
                clinica = medico.clinicas.get(id=id_clin)
                
                # Use service to handle complete prescription workflow
                prescription_service = PrescriptionService()
                pdf_response, processo_id = prescription_service.create_or_update_prescription(
                    form_data=dados_formulario,
                    user=usuario,
                    medico=medico,
                    clinica=clinica,
                    patient_exists=paciente_existe,
                    process_id=None  # New prescription
                )

                if pdf_response and processo_id:
                    # View layer handles file I/O operations
                    pdf_url = _save_pdf_for_serving(pdf_response, dados_formulario)
                    
                    if pdf_url:
                        # Extract filename from URL path for response
                        import os
                        filename = os.path.basename(pdf_url.rstrip('/'))
                        
                        request.session["processo_id"] = processo_id
                        logger.info(f"Prescription created successfully: Process {processo_id}")
                        
                        return JsonResponse({
                            'success': True,
                            'pdf_url': pdf_url,
                            'processo_id': processo_id,
                            'message': 'Processo criado com sucesso! PDF gerado.',
                            'filename': filename
                        })
                    else:
                        error_msg = 'Falha ao salvar PDF. Verifique se todos os arquivos necessários estão disponíveis.'
                        logger.error(f"PDF saving failed for user {usuario.email}")
                        
                        return JsonResponse({
                            'success': False,
                            'error': error_msg
                        })
                else:
                    error_msg = 'Falha ao gerar PDF. Verifique se todos os arquivos necessários estão disponíveis.'
                    logger.error(f"Prescription creation failed for user {usuario.email}")
                    
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'error': error_msg
                        })
                    else:
                        messages.error(request, error_msg)
                        return redirect("home")
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Erro de validação do formulário.',
                    'form_errors': formulario.errors
                })
        except IntegrityError as e:
            return JsonResponse({
                'success': False,
                'error': 'Este processo já existe para este paciente. Verifique se não há duplicatas.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erro ao processar formulário: {str(e)}'
            })
    
    # If this is a GET request, create a fresh form
    elif request.method == "GET":
        try:
            print(f"DEBUG CADASTRO: GET request - checking medico data")
            print(f"DEBUG CADASTRO: medico.crm_medico = {repr(medico.crm_medico)}")
            print(f"DEBUG CADASTRO: medico.cns_medico = {repr(medico.cns_medico)}")
            print(f"DEBUG CADASTRO: not medico.crm_medico = {not medico.crm_medico}")
            print(f"DEBUG CADASTRO: not medico.cns_medico = {not medico.cns_medico}")
            print(f"DEBUG CADASTRO: condition result = {not medico.crm_medico or not medico.cns_medico}")
            
            # Check if doctor has CRM and CNS first
            if not medico.crm_medico or not medico.cns_medico:
                print(f"DEBUG CADASTRO: Missing CRM/CNS, redirecting to complete-profile")
                messages.info(request, "Complete seus dados médicos antes de criar processos.")
                return redirect("complete-profile")
            
            # Then check if they have clinics
            if not usuario.clinicas.exists():
                messages.info(request, "Cadastre uma clínica antes de criar processos.")
                return redirect("clinicas-cadastro")
            # English: form - use setup data
            formulario = ModeloFormulario(escolhas, medicamentos, initial=setup.dados_iniciais)
        except Exception as e:
            messages.error(request, f"Erro ao carregar formulário de cadastro: {e}")
            return redirect("home")
    
    # Setup context for template rendering (only for GET requests)
    try:
        # English: conditional_fields
        campos_condicionais = extrair_campos_condicionais(formulario)
        # English: protocol_link
        link_protocolo = gerar_link_protocolo(setup.cid)
        
        # English: context
        contexto = {
            "formulario": formulario,
            "paciente_existe": paciente_existe,
            "campos_condicionais": campos_condicionais,
            "link_protocolo": link_protocolo,
        }
        
        # Add patient data if exists
        if paciente_existe:
            if "paciente_id" not in request.session:
                messages.error(request, "ID do paciente não encontrado na sessão.")
                return redirect("home")
            # English: patient_id
            paciente_id = request.session["paciente_id"]
            # English: patient
            paciente = Paciente.objects.get(id=paciente_id)
            contexto["paciente"] = paciente
            
            # Add conditional fields for existing patient using versioned data
            # Get user's versioned data
            user = request.user
            version = paciente.get_version_for_user(user)
            
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
            # English: patient_data
            dados_paciente["diagnostico"] = Doenca.objects.get(cid=setup.cid).nome
            # English: patient_data
            dados_paciente["cid"] = setup.cid
            # English: patient_data
            dados_paciente["data_1"] = setup.primeira_data
            # English: adjusted_fields
            campos_ajustados, _ = ajustar_campos_condicionais(dados_paciente)
            contexto.update(campos_ajustados)
        
        contexto.update(mostrar_med(False))
        return render(request, "processos/cadastro.html", contexto)
    except Exception as e:
        messages.error(request, f"Erro ao carregar formulário de cadastro: {e}")
        return redirect("home")


# pdf
@login_required
def pdf(request):
    """Displays the generated PDF.

    Args:
        request: The HTTP request.

    Returns:
        A rendered HTML page with a link to the PDF.
    """
    if request.method == "GET":
        # English: pdf_link
        link_pdf = request.session["path_pdf_final"]
        # English: context
        contexto = {"link_pdf": link_pdf}
        return render(request, "processos/pdf.html", contexto)


# serve pdf
@login_required
def serve_pdf(request, filename):
    """Serves PDF files securely with authentication and authorization.
    
    This view ensures that only authenticated users can access PDFs and that
    they can only access PDFs they are authorized to view. Authorization is
    verified by checking if the user has access to the patient whose CPF is
    embedded in the PDF filename.
    
    Args:
        request: The HTTP request.
        filename: The PDF filename to serve (format: pdf_final_{cpf}_{cid}.pdf).
    
    Returns:
        HttpResponse: The PDF file content with proper headers.
        
    Raises:
        Http404: If file doesn't exist or user lacks permission.
    """
    try:
        # Validate filename format for security
        if not filename.endswith('.pdf'):
            logger.warning(f"Invalid file type requested: {filename}")
            raise Http404("Invalid file type")
        
        # Basic filename validation to prevent directory traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            logger.warning(f"Directory traversal attempt: {filename}")
            raise Http404("Invalid filename")
        
        # Verify PDF filename follows expected pattern: pdf_final_{cpf}_{cid}.pdf
        if not filename.startswith('pdf_final_'):
            logger.warning(f"Invalid PDF filename pattern: {filename}")
            raise Http404("Invalid filename format")
        
        # Extract patient CPF from filename for authorization
        try:
            # Remove prefix 'pdf_final_' and suffix '.pdf'
            core_name = filename[10:-4]  # Remove 'pdf_final_' and '.pdf'
            parts = core_name.split('_')
            
            if len(parts) < 2:
                logger.warning(f"Invalid filename structure: {filename}")
                raise Http404("Invalid filename format")
            
            # First part is CPF, remaining parts form the CID
            cpf_raw = parts[0]
            
            # Clean CPF - remove dots and dashes to get only digits
            cpf_paciente = cpf_raw.replace('.', '').replace('-', '')
            
            # Verify CPF format (11 digits after cleaning)
            if not cpf_paciente.isdigit() or len(cpf_paciente) != 11:
                logger.warning(f"Invalid CPF format in filename: {cpf_raw} (cleaned: {cpf_paciente})")
                raise Http404("Invalid filename format")
            
        except (IndexError, ValueError) as e:
            logger.warning(f"Error parsing filename {filename}: {e}")
            raise Http404("Invalid filename format")
        
        # AUTHORIZATION: Verify user has access to this patient
        try:
            # Check if current user has access to patient with this CPF
            # Try both cleaned CPF and original formatted CPF from filename
            has_access = (
                request.user.pacientes.filter(cpf_paciente=cpf_paciente).exists() or
                request.user.pacientes.filter(cpf_paciente=cpf_raw).exists()
            )
            
            if not has_access:
                logger.warning(f"User {request.user.email} attempted unauthorized access to PDF for CPF {cpf_paciente}")
                raise Http404("Access denied")
            
            logger.info(f"User {request.user.email} authorized to access PDF for CPF {cpf_paciente}")
            
        except Exception as e:
            logger.error(f"Error during authorization check: {e}")
            raise Http404("Authorization error")
        
        # Serve the file from /tmp filesystem
        try:
            import os
            tmp_pdf_path = f"/tmp/{filename}"
            
            if os.path.exists(tmp_pdf_path):
                # Serve from filesystem
                with open(tmp_pdf_path, 'rb') as f:
                    pdf_content = f.read()
                
                response = HttpResponse(pdf_content, content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename="{filename}"'
                response['X-Content-Type-Options'] = 'nosniff'
                response['X-Frame-Options'] = 'SAMEORIGIN'
                
                logger.info(f"Successfully served PDF {filename} to user {request.user.email}")
                
                # Track PDF serving analytics
                try:
                    PDFGenerationLog.objects.create(
                        user=request.user,
                        pdf_type='served',
                        success=True,
                        generation_time_ms=0,  # No generation time for serving
                        file_size_bytes=len(pdf_content),
                        ip_address=request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0] if request.META.get('HTTP_X_FORWARDED_FOR') else request.META.get('REMOTE_ADDR'),
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        error_message=''
                    )
                except Exception as analytics_error:
                    logger.error(f"Error tracking PDF serving analytics: {analytics_error}")
                
                return response
            else:
                # File not found - PDF was not generated or expired
                logger.warning(f"PDF not found in filesystem: {tmp_pdf_path}")
                raise Http404("PDF not found or expired")
                
        except Exception as e:
            logger.error(f"Error serving PDF from filesystem: {e}")
            raise Http404("Error serving PDF")
            
    except Http404:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in serve_pdf: {e}")
        raise Http404("Server error")


@login_required
@csrf_exempt
def set_edit_session(request):
    """Set processo_id in session for editing"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            processo_id = data.get('processo_id')
            
            if not processo_id:
                return JsonResponse({'error': 'processo_id is required'}, status=400)
            
            # Verify user owns this process
            try:
                processo = Processo.objects.get(id=processo_id, usuario=request.user)
                request.session["processo_id"] = str(processo_id)
                request.session["cid"] = processo.doenca.cid
                logger.info(f"Set edit session for processo {processo_id}, user {request.user}")
                return JsonResponse({'success': True})
            except Processo.DoesNotExist:
                logger.warning(f"Process {processo_id} not found for user {request.user}")
                return JsonResponse({'error': 'Process not found'}, status=404)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Error setting edit session: {e}")
            return JsonResponse({'error': 'Server error'}, status=500)
    
    return JsonResponse({'error': 'Only POST method allowed'}, status=405)


def _save_pdf_for_serving(pdf_response, data):
    """
    Save PDF to filesystem for serving and return URL path.
    
    This is view-layer infrastructure logic, handling HTTP response processing
    and file system operations.
    
    Args:
        pdf_response: HttpResponse containing PDF data
        data: Prescription data for filename generation
        
    Returns:
        str: URL path for accessing the PDF, or None if save fails
    """
    try:
        # Generate filename
        cpf_paciente = data.get('cpf_paciente', 'unknown')
        cid = data.get('cid', 'unknown')
        filename = f"pdf_final_{cpf_paciente}_{cid}.pdf"
        
        # Save to /tmp for serving
        tmp_pdf_path = f"/tmp/{filename}"
        with open(tmp_pdf_path, 'wb') as f:
            f.write(pdf_response.content)
        
        # Generate URL path
        from django.urls import reverse
        pdf_url = reverse('processos-serve-pdf', kwargs={'filename': filename})
        
        logger.info(f"View layer: PDF saved to {tmp_pdf_path}")
        return pdf_url
        
    except Exception as e:
        logger.error(f"View layer: Failed to save PDF: {e}")
        return None
