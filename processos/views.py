from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.forms.models import model_to_dict
from datetime import date
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
            return redirect("processos-edicao")
        except Processo.DoesNotExist:
            messages.error(request, "Processo não encontrado ou você não tem permissão para acessá-lo.")
            return redirect("processos-busca")


@login_required
def edicao(request):
    usuario = request.user
    medico = seletor_medico(usuario)
    clinicas = medico.clinicas.all()
    escolhas = tuple([(c.id, c.nome_clinica) for c in clinicas])
    cid = request.session["cid"]
    medicamentos = listar_med(cid)
    ModeloFormulario = fabricar_formulario(cid, True)

    try:
        processo_id = request.session["processo_id"]
        # Verify user owns this process
        processo = Processo.objects.get(id=processo_id, usuario=usuario)
    except (KeyError, Processo.DoesNotExist):
        messages.error(request, "Processo não encontrado ou você não tem permissão para acessá-lo.")
        return redirect("processos-busca")

    try:
        primeira_data = request.session["data1"]
    except KeyError:
        primeira_data = date.today().strftime("%d/%m/%Y")

    if request.method == "POST":
        formulario = ModeloFormulario(escolhas, medicamentos, request.POST)

        if formulario.is_valid():
            dados_formulario = formulario.cleaned_data
            id_clin = dados_formulario["clinicas"]
            clinica = medico.clinicas.get(id=id_clin)

            ids_med_cadastrados = gerar_lista_meds_ids(dados_formulario)

            dados_formulario, meds_ids = gera_med_dosagem(
                dados_formulario, ids_med_cadastrados
            )

            # Registra os dados do médico logado e da clínica associada
            dados = vincula_dados_emissor(usuario, medico, clinica, dados_formulario)

            formulario.save(usuario, medico, processo_id, meds_ids)

            path_pdf_final = transfere_dados_gerador(dados)

            if path_pdf_final:
                request.session["path_pdf_final"] = path_pdf_final
                request.session["processo_id"] = processo_id
                return redirect("processos-pdf")
            else:
                messages.error(request, "Falha ao gerar PDF. Verifique se todos os arquivos necessários estão disponíveis.")
                return redirect("processos-cadastro")

    else:
        dados_iniciais = cria_dict_renovação(processo)
        dados_iniciais["data_1"] = primeira_data
        dados_iniciais["clinicas"] = dados_iniciais["clinica"].id
        dados_iniciais = resgatar_prescricao(dados_iniciais, processo)
        formulario = ModeloFormulario(escolhas, medicamentos, initial=dados_iniciais)
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
        busca = request.GET.get("b")
        usuario = request.user
        request.session["busca"] = busca
        pacientes_usuario = usuario.pacientes.all()
        busca_pacientes = pacientes_usuario.filter(
            (Q(nome_paciente__icontains=busca) | Q(cpf_paciente__icontains=busca))
        )

        contexto = {"busca_pacientes": busca_pacientes, "usuario": usuario}
        return render(request, "processos/renovacao_rapida.html", contexto)

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
            dados = gerar_dados_renovacao(nova_data, processo_id)
            path_pdf_final = transfere_dados_gerador(dados)
            
            if path_pdf_final:
                return redirect(path_pdf_final)
            else:
                print("ERROR: Failed to generate PDF for renewal")
                messages.error(request, "Falha ao gerar PDF. Verifique os logs do sistema.")
        except Exception as e:
            print(f"ERROR: Exception in renovacao_rapida: {e}")
            messages.error(request, f"Erro interno: {str(e)}")
        
        # On error, recreate the GET context and render the form again
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
    usuario = request.user
    medico = seletor_medico(usuario)
    clinicas = medico.clinicas.all()
    escolhas = tuple([(c.id, c.nome_clinica) for c in clinicas])
    paciente_existe = request.session["paciente_existe"]
    primeira_data = date.today().strftime("%d/%m/%Y")
    cid = request.session["cid"]
    medicamentos = listar_med(cid)
    ModeloFormulario = fabricar_formulario(cid, False)

    if request.method == "POST":
        formulario = ModeloFormulario(escolhas, medicamentos, request.POST)

        if formulario.is_valid():
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
                return redirect("processos-pdf")
            else:
                messages.error(request, "Falha ao gerar PDF. Verifique se todos os arquivos necessários estão disponíveis.")
                # Don't redirect, fall through to render the form again with error message
    else:
        if not usuario.clinicas.exists():
            return redirect("clinicas-cadastro")
        if paciente_existe:
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


@login_required
def pdf(request):
    if request.method == "GET":
        link_pdf = request.session["path_pdf_final"]
        contexto = {"link_pdf": link_pdf}
        return render(request, "processos/pdf.html", contexto)
