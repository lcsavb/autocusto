from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponse, Http404
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
from medicos.seletor import medico as seletor_medico
from pacientes.models import Paciente
from processos.models import Processo, Doenca
from .forms import (
    mostrar_med,
    ajustar_campos_condicionais,
    extrair_campos_condicionais,
    fabricar_formulario,
)
from .dados import (
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
        
        # Convert patient model to dictionary for form initialization
        # English: patient_data
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
    
    This view implements a complex workflow for Brazilian medical prescription renewals:
    1. Validates session state and user permissions
    2. Dynamically constructs form based on disease protocol
    3. Handles both GET (form display) and POST (form processing) requests
    4. Manages medication data and PDF generation
    
    The view includes extensive error handling and logging due to the critical nature
    of medical prescription data and the complexity of the Brazilian SUS system requirements.

    Critique:
    - This view is very long and complex. It would be better to split it into
      smaller, more focused functions. For example, the form processing logic
      could be moved to a separate function.
    - The error handling is very broad. It catches any exception and returns
      a generic error message. It would be better to catch specific exceptions
      and log them properly to make debugging easier.
    """
    try:
        logger.info(f"Edicao view started - User: {request.user}, Method: {request.method}")
        
        # English: user
        usuario = request.user
        logger.info(f"Usuario: {usuario}")
        
        # Get doctor record associated with current user
        # English: doctor
        medico = seletor_medico(usuario)
        logger.info(f"Medico: {medico}")
        
        # Get clinics available to this doctor for prescription issuance
        # English: clinics
        clinicas = medico.clinicas.all()
        logger.info(f"Clinicas count: {clinicas.count()}")
        
        # Create choices tuple for clinic selection dropdown
        # English: choices
        escolhas = tuple([(c.id, c.nome_clinica) for c in clinicas])
        logger.info(f"Escolhas: {escolhas}")
        
        # Get disease CID from session (set by home view workflow)
        cid = request.session["cid"]
        logger.info(f"CID from session: {cid}")
        
        # Get medications approved for this specific disease
        # English: medications
        medicamentos = listar_med(cid)
        logger.info(f"Medicamentos count: {len(medicamentos) if medicamentos else 0}")
        
        # Dynamically construct form class based on disease protocol
        # This is crucial because different diseases have different required fields
        # English: FormModel
        ModeloFormulario = fabricar_formulario(cid, True)  # True = renewal form
        logger.info(f"ModeloFormulario created: {ModeloFormulario}")
        
    except Exception as e:
        logger.error(f"Error in edicao view initialization: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        messages.error(request, f"Erro na inicialização: {str(e)}")
        return redirect("processos-busca")

    try:
        # English: process_id
        processo_id = request.session["processo_id"]
        logger.info(f"Processo ID from session: {processo_id}")
        
        # Verify user owns this process
        # English: process
        processo = Processo.objects.get(id=processo_id, usuario=usuario)
        logger.info(f"Processo found: {processo}")
        
    except (KeyError, Processo.DoesNotExist) as e:
        logger.error(f"Error getting processo: {str(e)}")
        messages.error(request, "Processo não encontrado ou você não tem permissão para acessá-lo.")
        return redirect("processos-busca")

    try:
        # English: first_date
        primeira_data = request.session["data1"]
        logger.info(f"Primeira data from session: {primeira_data}")
    except KeyError:
        # English: first_date
        primeira_data = date.today().strftime("%d/%m/%Y")
        logger.info(f"Using default primeira_data: {primeira_data}")

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
                    ids_med_cadastrados = gerar_lista_meds_ids(dados_formulario)
                    logger.info(f"Medication IDs generated: {ids_med_cadastrados}")
                    dados_formulario, meds_ids = gera_med_dosagem(dados_formulario, ids_med_cadastrados)
                    logger.info(f"Medication dosage generated, meds_ids: {meds_ids}")
                    dados = vincula_dados_emissor(usuario, medico, clinica, dados_formulario)
                    logger.info(f"Emissor data linked successfully")
                    formulario.save(usuario, medico, processo_id, meds_ids)
                    logger.info(f"Formulario saved successfully")
                    path_pdf_final = transfere_dados_gerador(dados)
                    logger.info(f"PDF path generated: {path_pdf_final}")
                    if path_pdf_final:
                        request.session["path_pdf_final"] = path_pdf_final
                        request.session["processo_id"] = processo_id
                        return JsonResponse({
                            'success': True,
                            'pdf_url': path_pdf_final,
                            'message': 'Processo atualizado com sucesso! PDF gerado.',
                            'filename': 'processo_atualizado.pdf'
                        })
                    else:
                        logger.error("Failed to generate PDF path")
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
        # English: initial_data
        dados_iniciais = cria_dict_renovação(processo)
        # English: initial_data
        dados_iniciais["data_1"] = primeira_data
        # English: initial_data
        dados_iniciais["clinicas"] = dados_iniciais["clinica"].id
        # English: initial_data
        dados_iniciais = resgatar_prescricao(dados_iniciais, processo)
        # English: form
        formulario = ModeloFormulario(escolhas, medicamentos, initial=dados_iniciais)
    
    # Set up variables needed for template rendering (for both GET and POST with validation errors)
    # English: conditional_fields
    campos_condicionais = extrair_campos_condicionais(formulario)
    # English: protocol_link
    link_protocolo = gerar_link_protocolo(cid)

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
                # English: search_patients
                busca_pacientes = pacientes_usuario.filter(
                    (Q(nome_paciente__icontains=busca) | Q(cpf_paciente__icontains=busca))
                )
            else:
                # English: search_patients
                busca_pacientes = pacientes_usuario.none()  # Empty queryset if no search
            
            print(f"DEBUG: busca_pacientes count = {busca_pacientes.count()}")

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
            print(f"\n=== RENOVACAO_RAPIDA PDF GENERATION START ===")
            print(f"DEBUG: processo_id: {processo_id}")
            print(f"DEBUG: nova_data: {nova_data}")
            
            # English: data
            data_start = time.time()
            dados = gerar_dados_renovacao(nova_data, processo_id)
            data_end = time.time()
            print(f"DEBUG: Generated renovation data successfully in {data_end - data_start:.3f}s")
            
            # English: final_pdf_path
            pdf_start = time.time()
            path_pdf_final = transfere_dados_gerador(dados)
            pdf_end = time.time()
            total_time = pdf_end - start_time
            print(f"DEBUG: transfere_dados_gerador returned: {path_pdf_final} in {pdf_end - pdf_start:.3f}s")
            print(f"DEBUG: Total PDF generation time: {total_time:.3f}s")
            
            if path_pdf_final:
                # Check if this is an AJAX request
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    # Return JSON response for AJAX
                    return JsonResponse({
                        'success': True,
                        'pdf_url': path_pdf_final,
                        'message': 'Renovação processada com sucesso! PDF gerado.',
                        'filename': 'renovacao_processo.pdf'
                    })
                else:
                    # Traditional redirect for non-AJAX requests
                    messages.success(request, "Renovação processada com sucesso! PDF gerado.")
                    return redirect(path_pdf_final)
            else:
                print("ERROR: Failed to generate PDF for renewal")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': 'Falha ao gerar PDF. Verifique os logs do sistema.'
                    })
                else:
                    messages.error(request, "Falha ao gerar PDF. Verifique os logs do sistema.")
        except Exception as e:
            print(f"ERROR: Exception in renovacao_rapida: {e}")
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
        # English: search_patients
        busca_pacientes = pacientes_usuario.filter(
            (Q(nome_paciente__icontains=busca) | Q(cpf_paciente__icontains=busca))
        )
        # English: context
        contexto = {"busca_pacientes": busca_pacientes, "usuario": usuario}
        return render(request, "processos/renovacao_rapida.html", contexto)


# registration
@login_required
def cadastro(request):
    """Handles the registration of new medical prescription processes.

    This view implements a complex workflow for creating new Brazilian medical
    prescriptions:
    1. Validates session state and user permissions
    2. Dynamically constructs form based on disease protocol
    3. Handles both GET (form display) and POST (form processing) requests
    4. Manages medication data and PDF generation

    The view includes extensive error handling and logging due to the critical
    nature of medical prescription data and the complexity of the Brazilian SUS
    system requirements.

    Critique:
    - This view is very long and complex. It would be better to split it into
      smaller, more focused functions. For example, the form processing logic
      could be moved to a separate function.
    - The error handling is very broad. It catches any exception and returns
      a generic error message. It would be better to catch specific exceptions
      and log them properly to make debugging easier.
    """
    try:
        # English: user
        usuario = request.user
        # English: doctor
        medico = seletor_medico(usuario)
        # English: clinics
        clinicas = medico.clinicas.all()
        # English: choices
        escolhas = tuple([(c.id, c.nome_clinica) for c in clinicas])
        
        # Check for required session variables
        if "paciente_existe" not in request.session:
            messages.error(request, "Sessão expirada. Por favor, inicie o cadastro novamente.")
            return redirect("processos-home")
        
        if "cid" not in request.session:
            messages.error(request, "CID não encontrado na sessão. Por favor, selecione o diagnóstico novamente.")
            return redirect("processos-home")
            
        # English: patient_exists
        paciente_existe = request.session["paciente_existe"]
        # English: first_date
        primeira_data = date.today().strftime("%d/%m/%Y")
        cid = request.session["cid"]
        # English: medications
        medicamentos = listar_med(cid)
        # English: FormModel
        ModeloFormulario = fabricar_formulario(cid, False)
    except Exception as e:
        messages.error(request, f"Erro ao carregar dados do cadastro: {e}")
        return redirect("processos-home")

    if request.method == "POST":
        # Since the template ALWAYS sends AJAX requests, we ALWAYS return JSON
        try:
            # English: form
            formulario = ModeloFormulario(escolhas, medicamentos, request.POST)

            if formulario.is_valid():
                # English: form_data
                dados_formulario = formulario.cleaned_data
                # English: clinic_id
                id_clin = dados_formulario["clinicas"]
                # English: clinic
                clinica = medico.clinicas.get(id=id_clin)

                # English: registered_medication_ids
                ids_med_cadastrados = gerar_lista_meds_ids(dados_formulario)
                # English: form_data, medication_ids
                dados_formulario, meds_ids = gera_med_dosagem(
                    dados_formulario, ids_med_cadastrados
                )
                # English: data
                dados = vincula_dados_emissor(usuario, medico, clinica, dados_formulario)
                # English: process_id
                processo_id = formulario.save(usuario, medico, meds_ids)
                # English: final_pdf_path
                path_pdf_final = transfere_dados_gerador(dados)

                if path_pdf_final:
                    import os
                    filename = os.path.basename(path_pdf_final)
                    from django.urls import reverse
                    #pdf_url = reverse('processos-serve-pdf', args=[filename])
                    #request.session["path_pdf_final"] = path_pdf_final
                    request.session["processo_id"] = processo_id
                    return JsonResponse({
                        'success': True,
                        'pdf_url': path_pdf_final,
                        'message': 'Processo criado com sucesso! PDF gerado.',
                        'filename': filename
                    })
                else:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'error': 'Falha ao gerar PDF. Verifique se todos os arquivos necessários estão disponíveis.'
                        })
                    else:
                        messages.error(request, "Falha ao gerar PDF. Verifique se todos os arquivos necessários estão disponíveis.")
                        return redirect("processos-home")
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
            # Check if doctor has CRM and CNS first
            if not medico.crm_medico or not medico.cns_medico:
                messages.info(request, "Complete seus dados médicos antes de criar processos.")
                return redirect("complete-profile")
            
            # Then check if they have clinics
            if not usuario.clinicas.exists():
                messages.info(request, "Cadastre uma clínica antes de criar processos.")
                return redirect("clinicas-cadastro")
            # English: initial_data
            dados_iniciais = _get_initial_data(request, paciente_existe, primeira_data, cid)
            # English: form
            formulario = ModeloFormulario(escolhas, medicamentos, initial=dados_iniciais)
        except Exception as e:
            messages.error(request, f"Erro ao carregar formulário de cadastro: {e}")
            return redirect("processos-home")
    
    # Setup context for template rendering (only for GET requests)
    try:
        # English: conditional_fields
        campos_condicionais = extrair_campos_condicionais(formulario)
        # English: protocol_link
        link_protocolo = gerar_link_protocolo(cid)
        
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
                return redirect("processos-home")
            # English: patient_id
            paciente_id = request.session["paciente_id"]
            # English: patient
            paciente = Paciente.objects.get(id=paciente_id)
            contexto["paciente"] = paciente
            
            # Add conditional fields for existing patient
            # English: patient_data
            dados_paciente = model_to_dict(paciente)
            # English: patient_data
            dados_paciente["diagnostico"] = Doenca.objects.get(cid=cid).nome
            # English: patient_data
            dados_paciente["cid"] = cid
            # English: patient_data
            dados_paciente["data_1"] = primeira_data
            # English: adjusted_fields
            campos_ajustados, _ = ajustar_campos_condicionais(dados_paciente)
            contexto.update(campos_ajustados)
        
        contexto.update(mostrar_med(False))
        return render(request, "processos/cadastro.html", contexto)
    except Exception as e:
        messages.error(request, f"Erro ao carregar formulário de cadastro: {e}")
        return redirect("processos-home")


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
