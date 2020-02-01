from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.conf import settings
from django.db.models import Q
from django.forms.models import model_to_dict
from datetime import date
from medicos.models import Medico
from medicos.seletor import medico as seletor_medico
from pacientes.models import Paciente
from processos.models import Processo
from usuarios.models import Usuario
from clinicas.models import Clinica, Emissor
from .forms import NovoProcesso, RenovarProcesso
import os
import pypdftk
from .manejo_pdfs import GeradorPDF
from .dados import cria_dict_renovação, gerar_dados_renovacao, vincula_dados_emissor, transfere_dados_gerador, mostrar_med

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
        return redirect('processos-edicao')


@login_required
def edicao(request):
    usuario = request.user
    medico = seletor_medico(usuario)
    clinicas = medico.clinicas.all()
    escolhas = tuple([(c.id, c.nome_clinica) for c in clinicas])

    try:
        processo_id = request.session['processo_id']
    except:
        raise ValueError
        # BUG FALHA DE SEGURANÇA ENVIAR ID VIA GET
        # processo_id = request.GET.get('id')
    
    try:
        primeira_data = request.session['data1']
    except:
        primeira_data = date.today().strftime('%d/%m/%Y')
    
    if request.method == 'POST':
        formulario = RenovarProcesso(escolhas, request.POST)    
            
        if formulario.is_valid():   
            dados_formulario = formulario.cleaned_data
            id_clin = dados_formulario['clinicas']
            clinica = medico.clinicas.get(id=id_clin)

            # Registra os dados do médico logado e da clínica associada
            dados = vincula_dados_emissor(usuario, medico, clinica, dados_formulario)

            # Jeitinho, ainda não existem dados condicionais
            dados_condicionais = {}

            formulario.save(processo_id)

            path_pdf_final = transfere_dados_gerador(dados,dados_condicionais)
            return redirect(path_pdf_final)

    else:
        processo = Processo.objects.get(id=processo_id)
        dados_iniciais = cria_dict_renovação(processo)
        dados_iniciais['data_1'] = primeira_data
        dados_iniciais['clinicas'] = dados_iniciais['clinica'].id
        formulario = RenovarProcesso(escolhas, initial=dados_iniciais)

    contexto = {'formulario': formulario, 'processo': processo}
    contexto.update(mostrar_med(True,dados_iniciais['med2'],dados_iniciais['med3'],
                                dados_iniciais['med4'],dados_iniciais['med5']))  

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
    
    if request.method == 'POST':
        formulario = NovoProcesso(escolhas, request.POST)    
            
        if formulario.is_valid():   
            dados_formulario = formulario.cleaned_data
            id_clin = dados_formulario['clinicas']
            clinica = medico.clinicas.get(id=id_clin)

            dados = vincula_dados_emissor(usuario,medico,clinica,dados_formulario)

            # Jeitinho, ainda não existem dados condicionais
            dados_condicionais = {}

            formulario.save(usuario, medico)

            path_pdf_final = transfere_dados_gerador(dados,dados_condicionais)

            return redirect(path_pdf_final)
    else:
        if not usuario.clinicas.exists():
            return redirect('clinicas-cadastro')
        if paciente_existe:
                paciente_id = request.session['paciente_id']
                paciente = Paciente.objects.get(id=paciente_id)
                dados_paciente = model_to_dict(paciente)
                dados_paciente['cid'] = request.session['cid']
                dados_paciente['data_1'] = primeira_data
                formulario = NovoProcesso(escolhas, initial=dados_paciente)
                contexto = {'formulario': formulario, 
                            'paciente_existe': paciente_existe,
                            'paciente': paciente}
        else:
            dados_iniciais = {'cpf_paciente': request.session['cpf_paciente'],
                              'cid': request.session['cid'],
                              'data_1': primeira_data
                             }     
            formulario = NovoProcesso(escolhas, initial=dados_iniciais)
            contexto = {'formulario': formulario,
                        'paciente_existe': paciente_existe}
        
        contexto.update(mostrar_med(False))

        return render(request, 'processos/cadastro.html', contexto)  

    