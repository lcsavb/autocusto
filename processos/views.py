from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.conf import settings
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import JsonResponse
from datetime import date
from medicos.models import Medico
from medicos.seletor import medico as seletor_medico
from pacientes.models import Paciente
from processos.models import Processo, Protocolo, Medicamento, Doenca
from usuarios.models import Usuario
from clinicas.models import Clinica, Emissor
from .forms import NovoProcesso, RenovarProcesso, mostrar_med, ajustar_campos_condicionais, extrair_campos_condicionais, fabricar_formulario
import os
import pypdftk
from .manejo_pdfs import GeradorPDF
from .dados import (cria_dict_renovação,
                    gerar_dados_renovacao,
                    vincula_dados_emissor,
                    transfere_dados_gerador,
                    listar_med, gera_med_dosagem,
                    resgatar_prescricao,
                    gerar_lista_meds_ids,
                    gerar_link_protocolo)

@login_required
def busca_processos(request):
    if request.method == 'GET':
        usuario = request.user
        pacientes_usuario = usuario.pacientes.all()

        contexto = {'pacientes_usuario': pacientes_usuario,
                    'usuario': usuario
                    }
        return render(request, 'processos/busca.html', contexto)
    else:
        processo_id = request.POST.get('processo_id')
        request.session['processo_id'] = processo_id
        processo = Processo.objects.get(id=processo_id)
        request.session['cid'] = processo.doenca.cid
        return redirect('processos-edicao')


@login_required
def edicao(request):
    usuario = request.user
    medico = seletor_medico(usuario)
    clinicas = medico.clinicas.all()
    escolhas = tuple([(c.id, c.nome_clinica) for c in clinicas])
    cid = request.session['cid']
    medicamentos = listar_med(cid)
    ModeloFormulario = fabricar_formulario(cid,True)

    try:
        processo_id = request.session['processo_id']
        processo = Processo.objects.get(id=processo_id)
    except:
        raise ValueError
    
    try:
        primeira_data = request.session['data1']
    except:
        primeira_data = date.today().strftime('%d/%m/%Y')
    
    if request.method == 'POST':
        formulario = ModeloFormulario(escolhas, medicamentos, request.POST)    
            
        if formulario.is_valid():   
            dados_formulario = formulario.cleaned_data
            id_clin = dados_formulario['clinicas']
            clinica = medico.clinicas.get(id=id_clin)

            ids_med_cadastrados = gerar_lista_meds_ids(dados_formulario)
          
            dados_formulario, meds_ids = gera_med_dosagem(dados_formulario,ids_med_cadastrados)

            # Registra os dados do médico logado e da clínica associada
            dados = vincula_dados_emissor(usuario, medico, clinica, dados_formulario)

            # Jeitinho, ainda não existem dados condicionais
            dados_condicionais = {}

            formulario.save(usuario, medico, processo_id, meds_ids)

            path_pdf_final = transfere_dados_gerador(dados,dados_condicionais)
            return redirect(path_pdf_final)

    else:
        dados_iniciais = cria_dict_renovação(processo)
        dados_iniciais['data_1'] = primeira_data
        dados_iniciais['clinicas'] = dados_iniciais['clinica'].id
        dados_iniciais = resgatar_prescricao(dados_iniciais, processo)
        formulario = ModeloFormulario(escolhas, medicamentos, initial=dados_iniciais)
        campos_condicionais = extrair_campos_condicionais(formulario)
        link_protocolo = gerar_link_protocolo(cid)

    contexto = {'formulario': formulario,
                'processo': processo,
                'campos_condicionais': campos_condicionais,
                'link_protocolo': link_protocolo}
    contexto.update(mostrar_med(True,processo))

    return render(request, 'processos/edicao.html', contexto)




@login_required
def renovacao_rapida(request):
    if request.method == 'GET':
        busca = request.GET.get('b')
        usuario = request.user
        pacientes_usuario = usuario.pacientes.all()
        busca_pacientes = pacientes_usuario.filter(
            (Q(nome_paciente__icontains=busca) | Q(cpf_paciente__icontains=busca)))

        contexto = {'busca_pacientes': busca_pacientes, 'usuario': usuario}
        return render(request, 'processos/renovacao_rapida.html', contexto)

    else:
        processo_id = request.POST.get('processo_id')
        nova_data = request.POST.get('data_1')

        try:
            if request.POST['edicao'] == 'on':
                request.session['processo_id'] = processo_id
                request.session['data1'] = nova_data
                return redirect('processos-edicao')
        except:        
            dados = gerar_dados_renovacao(nova_data,processo_id)
            dados_condicionais = {}
            path_pdf_final = transfere_dados_gerador(dados,dados_condicionais)
            return redirect(path_pdf_final)
        

@login_required
def cadastro(request):
    usuario = request.user
    medico = seletor_medico(usuario)
    clinicas = medico.clinicas.all()
    escolhas = tuple([(c.id, c.nome_clinica) for c in clinicas])
    paciente_existe = request.session['paciente_existe']
    primeira_data = date.today().strftime('%d/%m/%Y')
    cid = request.session['cid']
    medicamentos = listar_med(cid)
    ModeloFormulario = fabricar_formulario(cid,False)    
    
    if request.method == 'POST':
        formulario = ModeloFormulario(escolhas, medicamentos, request.POST)    
        print('aqui')

        print(formulario.is_valid())
            
        if formulario.is_valid():   
            dados_formulario = formulario.cleaned_data
            print(dados_formulario)
            id_clin = dados_formulario['clinicas']
            clinica = medico.clinicas.get(id=id_clin)

            ids_med_cadastrados = gerar_lista_meds_ids(dados_formulario)
            dados_formulario, meds_ids = gera_med_dosagem(dados_formulario,ids_med_cadastrados)
            dados = vincula_dados_emissor(usuario,medico,clinica,dados_formulario)
            dados_condicionais = {}
            formulario.save(usuario, medico, meds_ids)
            path_pdf_final = transfere_dados_gerador(dados,dados_condicionais)

            return redirect(path_pdf_final)
    else:
        if not usuario.clinicas.exists():
            return redirect('clinicas-cadastro')
        if paciente_existe:
            paciente_id = request.session['paciente_id']
            paciente = Paciente.objects.get(id=paciente_id)
            dados_paciente = model_to_dict(paciente)
            dados_paciente['diagnostico'] = Doenca.objects.get(cid=cid).nome
            dados_paciente['cid'] = request.session['cid']
            dados_paciente['data_1'] = primeira_data
            campos_ajustados, dados_paciente = ajustar_campos_condicionais(dados_paciente)
            formulario = ModeloFormulario(escolhas, medicamentos, initial=dados_paciente)
            campos_condicionais = extrair_campos_condicionais(formulario)
            link_protocolo = gerar_link_protocolo(cid)
            contexto = {'formulario': formulario, 
                        'paciente_existe': paciente_existe,
                        'paciente': paciente,
                        'campos_condicionais': campos_condicionais,
                        'link_protocolo': link_protocolo
                        }
            contexto.update(campos_ajustados)
        else:
            link_protocolo = gerar_link_protocolo(cid)
            dados_iniciais = {'cpf_paciente': request.session['cpf_paciente'],
                              'data_1': primeira_data,
                              'cid': cid,
                              'diagnostico': Doenca.objects.get(cid=cid).nome
                             }

            formulario = ModeloFormulario(escolhas,medicamentos,initial=dados_iniciais)
            campos_condicionais = extrair_campos_condicionais(formulario)


            contexto = {'formulario': formulario,
                        'paciente_existe': paciente_existe,
                        'campos_condicionais': campos_condicionais,
                        'link_protocolo': link_protocolo
                        }
        
        contexto.update(mostrar_med(False))

        return render(request, 'processos/cadastro.html', contexto)  


