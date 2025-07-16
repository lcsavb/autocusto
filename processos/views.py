from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.forms.models import model_to_dict
from datetime import date
import logging
import traceback

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


@login_required
def busca_processos(request):
    if request.method == "GET":
        usuario = request.user
        pacientes_usuario = usuario.pacientes.all()

        contexto = {"pacientes_usuario": pacientes_usuario, "usuario": usuario}
        return render(request, "processos/busca.html", contexto)
    else:
        processo_id = request.POST.get("processo_id")
        # Verify user owns this process
        try:
            processo = Processo.objects.get(id=processo_id, usuario=request.user)
            request.session["processo_id"] = processo_id
            request.session["cid"] = processo.doenca.cid
            messages.success(request, f"Processo selecionado: {processo.doenca.nome}")
            return redirect("processos-edicao")
        except Processo.DoesNotExist:
            messages.error(request, "Processo não encontrado ou você não tem permissão para acessá-lo.")
            return redirect("processos-busca")


@login_required
def edicao(request):
    try:
        logger.info(f"Edicao view started - User: {request.user}, Method: {request.method}")
        
        usuario = request.user
        logger.info(f"Usuario: {usuario}")
        
        medico = seletor_medico(usuario)
        logger.info(f"Medico: {medico}")
        
        clinicas = medico.clinicas.all()
        logger.info(f"Clinicas count: {clinicas.count()}")
        
        escolhas = tuple([(c.id, c.nome_clinica) for c in clinicas])
        logger.info(f"Escolhas: {escolhas}")
        
        cid = request.session["cid"]
        logger.info(f"CID from session: {cid}")
        
        medicamentos = listar_med(cid)
        logger.info(f"Medicamentos count: {len(medicamentos) if medicamentos else 0}")
        
        ModeloFormulario = fabricar_formulario(cid, True)
        logger.info(f"ModeloFormulario created: {ModeloFormulario}")
        
    except Exception as e:
        logger.error(f"Error in edicao view initialization: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        messages.error(request, f"Erro na inicialização: {str(e)}")
        return redirect("processos-busca")

    try:
        processo_id = request.session["processo_id"]
        logger.info(f"Processo ID from session: {processo_id}")
        
        # Verify user owns this process
        processo = Processo.objects.get(id=processo_id, usuario=usuario)
        logger.info(f"Processo found: {processo}")
        
    except (KeyError, Processo.DoesNotExist) as e:
        logger.error(f"Error getting processo: {str(e)}")
        messages.error(request, "Processo não encontrado ou você não tem permissão para acessá-lo.")
        return redirect("processos-busca")

    try:
        primeira_data = request.session["data1"]
        logger.info(f"Primeira data from session: {primeira_data}")
    except KeyError:
        primeira_data = date.today().strftime("%d/%m/%Y")
        logger.info(f"Using default primeira_data: {primeira_data}")

    if request.method == "POST":
        logger.info("Processing POST request")
        
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

                    dados_formulario, meds_ids = gera_med_dosagem(
                        dados_formulario, ids_med_cadastrados
                    )
                    logger.info(f"Medication dosage generated, meds_ids: {meds_ids}")

                    # Registra os dados do médico logado e da clínica associada
                    dados = vincula_dados_emissor(usuario, medico, clinica, dados_formulario)
                    logger.info(f"Emissor data linked successfully")

                    formulario.save(usuario, medico, processo_id, meds_ids)
                    logger.info(f"Formulario saved successfully")

                    path_pdf_final = transfere_dados_gerador(dados)
                    logger.info(f"PDF path generated: {path_pdf_final}")

                    if path_pdf_final:
                        request.session["path_pdf_final"] = path_pdf_final
                        request.session["processo_id"] = processo_id
                        messages.success(request, "Processo atualizado com sucesso! PDF gerado.")
                        return redirect("processos-pdf")
                    else:
                        logger.error("Failed to generate PDF path")
                        messages.error(request, "Falha ao gerar PDF. Verifique se todos os arquivos necessários estão disponíveis.")
                        return redirect("processos-cadastro")
                        
                except Exception as e:
                    logger.error(f"Error in form processing: {str(e)}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    messages.error(request, f"Erro no processamento dos dados: {str(e)}")
                    return redirect("processos-busca")
                    
            else:
                logger.error(f"Formulario validation failed: {formulario.errors}")
                # Form validation failed - add errors as Django messages for toast display
                for field, errors in formulario.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
                        
        except Exception as e:
            logger.error(f"Error in POST processing: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            messages.error(request, f"Erro no processamento: {str(e)}")
            # Create a new form instance for template rendering when there's an exception
            dados_iniciais = cria_dict_renovação(processo)
            dados_iniciais["data_1"] = primeira_data
            dados_iniciais["clinicas"] = dados_iniciais["clinica"].id
            dados_iniciais = resgatar_prescricao(dados_iniciais, processo)
            formulario = ModeloFormulario(escolhas, medicamentos, initial=dados_iniciais)

    else:
        dados_iniciais = cria_dict_renovação(processo)
        dados_iniciais["data_1"] = primeira_data
        dados_iniciais["clinicas"] = dados_iniciais["clinica"].id
        dados_iniciais = resgatar_prescricao(dados_iniciais, processo)
        formulario = ModeloFormulario(escolhas, medicamentos, initial=dados_iniciais)
    
    # Set up variables needed for template rendering (for both GET and POST with validation errors)
    campos_condicionais = extrair_campos_condicionais(formulario)
    link_protocolo = gerar_link_protocolo(cid)

    contexto = {
        "formulario": formulario,
        "processo": processo,
        "campos_condicionais": campos_condicionais,
        "link_protocolo": link_protocolo,
    }
    contexto.update(mostrar_med(True, processo))

    return render(request, "processos/edicao.html", contexto)


@login_required
def renovacao_rapida(request):
    if request.method == "GET":
        try:
            print(f"DEBUG: GET request to renovacao_rapida")
            busca = request.GET.get("b")
            print(f"DEBUG: busca parameter = '{busca}'")
            
            usuario = request.user
            print(f"DEBUG: usuario = {usuario}")
            
            request.session["busca"] = busca
            
            pacientes_usuario = usuario.pacientes.all()
            print(f"DEBUG: pacientes_usuario count = {pacientes_usuario.count()}")
            
            if busca:
                busca_pacientes = pacientes_usuario.filter(
                    (Q(nome_paciente__icontains=busca) | Q(cpf_paciente__icontains=busca))
                )
            else:
                busca_pacientes = pacientes_usuario.none()  # Empty queryset if no search
            
            print(f"DEBUG: busca_pacientes count = {busca_pacientes.count()}")

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
        processo_id = request.POST.get("processo_id")
        nova_data = request.POST.get("data_1")

        # Check if user wants to edit the process
        if request.POST.get("edicao"):
            request.session["processo_id"] = processo_id
            request.session["cid"] = Processo.objects.get(id=processo_id).doenca.cid
            request.session["data1"] = nova_data
            return redirect("processos-edicao")
        
        # Generate PDF for renewal
        try:
            print(f"\n=== RENOVACAO_RAPIDA PDF GENERATION START ===")
            print(f"DEBUG: processo_id: {processo_id}")
            print(f"DEBUG: nova_data: {nova_data}")
            
            dados = gerar_dados_renovacao(nova_data, processo_id)
            print(f"DEBUG: Generated renovation data successfully")
            
            path_pdf_final = transfere_dados_gerador(dados)
            print(f"DEBUG: transfere_dados_gerador returned: {path_pdf_final}")
            
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
        busca = request.session.get("busca", "")
        usuario = request.user
        pacientes_usuario = usuario.pacientes.all()
        busca_pacientes = pacientes_usuario.filter(
            (Q(nome_paciente__icontains=busca) | Q(cpf_paciente__icontains=busca))
        )
        contexto = {"busca_pacientes": busca_pacientes, "usuario": usuario}
        return render(request, "processos/renovacao_rapida.html", contexto)


@login_required
def cadastro(request):
    try:
        usuario = request.user
        medico = seletor_medico(usuario)
        clinicas = medico.clinicas.all()
        escolhas = tuple([(c.id, c.nome_clinica) for c in clinicas])
        
        # Check for required session variables
        if "paciente_existe" not in request.session:
            messages.error(request, "Sessão expirada. Por favor, inicie o cadastro novamente.")
            return redirect("processos-home")
        
        if "cid" not in request.session:
            messages.error(request, "CID não encontrado na sessão. Por favor, selecione o diagnóstico novamente.")
            return redirect("processos-home")
            
        paciente_existe = request.session["paciente_existe"]
        primeira_data = date.today().strftime("%d/%m/%Y")
        cid = request.session["cid"]
        medicamentos = listar_med(cid)
        ModeloFormulario = fabricar_formulario(cid, False)
    except Exception as e:
        messages.error(request, f"Erro ao carregar dados do cadastro: {e}")
        return redirect("processos-home")

    if request.method == "POST":
        try:
            formulario = ModeloFormulario(escolhas, medicamentos, request.POST)

            if formulario.is_valid():
                try:
                    dados_formulario = formulario.cleaned_data
                    id_clin = dados_formulario["clinicas"]
                    clinica = medico.clinicas.get(id=id_clin)

                    ids_med_cadastrados = gerar_lista_meds_ids(dados_formulario)
                    dados_formulario, meds_ids = gera_med_dosagem(
                        dados_formulario, ids_med_cadastrados
                    )
                    dados = vincula_dados_emissor(usuario, medico, clinica, dados_formulario)
                    processo_id = formulario.save(usuario, medico, meds_ids)
                    path_pdf_final = transfere_dados_gerador(dados)

                    if path_pdf_final:
                        request.session["path_pdf_final"] = path_pdf_final
                        request.session["processo_id"] = processo_id
                        messages.success(request, "Processo criado com sucesso! PDF gerado.")
                        return redirect("processos-pdf")
                    else:
                        messages.error(request, "Falha ao gerar PDF. Verifique se todos os arquivos necessários estão disponíveis.")
                        # Don't redirect, fall through to render the form again with error message
                except Exception as e:
                    messages.error(request, f"Erro ao processar dados do formulário: {e}")
                    # Fall through to render form again
            else:
                # Form validation failed - add errors as Django messages for toast display
                for field, errors in formulario.errors.items():
                    for error in errors:
                        messages.error(request, error)
                # Redirect to avoid POST-redirect-GET issue
                return redirect("processos-cadastro")
        except Exception as e:
            messages.error(request, f"Erro ao processar formulário: {e}")
            return redirect("processos-cadastro")
    else:
        try:
            if not usuario.clinicas.exists():
                return redirect("clinicas-cadastro")
            if paciente_existe:
                if "paciente_id" not in request.session:
                    messages.error(request, "ID do paciente não encontrado na sessão.")
                    return redirect("processos-home")
                    
                paciente_id = request.session["paciente_id"]
                paciente = Paciente.objects.get(id=paciente_id)
                dados_paciente = model_to_dict(paciente)
                dados_paciente["diagnostico"] = Doenca.objects.get(cid=cid).nome
                dados_paciente["cid"] = request.session["cid"]
                dados_paciente["data_1"] = primeira_data
                campos_ajustados, dados_paciente = ajustar_campos_condicionais(
                    dados_paciente
                )
                formulario = ModeloFormulario(
                    escolhas, medicamentos, initial=dados_paciente
                )
                campos_condicionais = extrair_campos_condicionais(formulario)
                link_protocolo = gerar_link_protocolo(cid)
                contexto = {
                    "formulario": formulario,
                    "paciente_existe": paciente_existe,
                    "paciente": paciente,
                    "campos_condicionais": campos_condicionais,
                    "link_protocolo": link_protocolo,
                }
                contexto.update(campos_ajustados)
            else:
                if "cpf_paciente" not in request.session:
                    messages.error(request, "CPF do paciente não encontrado na sessão.")
                    return redirect("processos-home")
                    
                link_protocolo = gerar_link_protocolo(cid)
                dados_iniciais = {
                    "cpf_paciente": request.session["cpf_paciente"],
                    "data_1": primeira_data,
                    "cid": cid,
                    "diagnostico": Doenca.objects.get(cid=cid).nome,
                }

                formulario = ModeloFormulario(
                    escolhas, medicamentos, initial=dados_iniciais
                )
                campos_condicionais = extrair_campos_condicionais(formulario)

                contexto = {
                    "formulario": formulario,
                    "paciente_existe": paciente_existe,
                    "campos_condicionais": campos_condicionais,
                    "link_protocolo": link_protocolo,
                }

            contexto.update(mostrar_med(False))

            return render(request, "processos/cadastro.html", contexto)
        except Exception as e:
            messages.error(request, f"Erro ao carregar formulário de cadastro: {e}")
            return redirect("processos-home")


@login_required
def pdf(request):
    if request.method == "GET":
        link_pdf = request.session["path_pdf_final"]
        contexto = {"link_pdf": link_pdf}
        return render(request, "processos/pdf.html", contexto)
