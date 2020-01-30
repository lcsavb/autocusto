from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.conf import settings
from django.db.models import Q
from django.forms.models import model_to_dict
from medicos.models import Medico
from pacientes.models import Paciente
from processos.models import Processo
from usuarios.models import Usuario
from clinicas.models import Clinica, Emissor
from .forms import NovoProcesso, RenovarProcesso
import os
import pypdftk
from .manejo_pdfs import GeradorPDF
from .dados import cria_dict_renovação, gerar_dados_renovacao, vincula_dados_emissor, transfere_dados_gerador

class BuscaProcessos(LoginRequiredMixin, ListView):
    model = Paciente
    template_name = 'processos/busca.html'
    login_url = '/login/'
    raise_exception = True

    def get_queryset(self):
        return Paciente.objects.filter(usuario=self.request.user)


@login_required
def edicao(request):
    usuario = request.user
    medico = usuario.medico
    clinicas = medico.clinicas.all()
    escolhas = tuple([(c.id, c.nome_clinica) for c in clinicas])

    try:
        processo_id = request.session['processo_id']
    except:
        # BUG POSSÍVEL FALHA DE SEGURANÇA ENVIAR ID VIA GET
        processo_id = request.GET.get('id')

    
    if request.method == 'POST':
        formulario = RenovarProcesso(escolhas, request.POST)    
            
        if formulario.is_valid():   
            dados_formulario = formulario.cleaned_data
            id_clin = dados_formulario['clinicas']
            clinica = medico.clinicas.get(id=id_clin)

            # Registra os dados do médico logado e da clínica associada
            dados = vincula_dados_emissor(medico,clinica,dados_formulario)

            # Jeitinho, ainda não existem dados condicionais
            dados_condicionais = {}

            formulario.save(processo_id)

            path_pdf_final = transfere_dados_gerador(dados,dados_condicionais)
            return redirect(path_pdf_final)

    else:
        processo = Processo.objects.get(id=processo_id)
        dados_iniciais = cria_dict_renovação(processo)
        formulario = RenovarProcesso(escolhas, initial=dados_iniciais)

    contexto = {'formulario': formulario, 'processo': processo}  

    return render(request, 'processos/edicao.html', contexto)




@login_required
def renovacao_rapida(request):
    if request.method == 'GET':
        busca = request.GET.get('b')
        pacientes = Paciente.objects.filter(Q(usuario=request.user)
        & (Q(nome_paciente__icontains=busca) & Q(cpf_paciente__icontains=busca)))


        contexto = {'pacientes': pacientes}
        return render(request, 'processos/renovacao_rapida.html', contexto)

    else:
        print(request.POST) 
        processo_id = request.POST.get('processo_id')
        nova_data = request.POST.get('data_1')

        dados = gerar_dados_renovacao(nova_data,processo_id)
        dados_condicionais = {}
        
        path_pdf_final = transfere_dados_gerador(dados,dados_condicionais)
        return redirect(path_pdf_final)
        

@login_required
def cadastro(request):
    usuario = request.user
    medico = request.user.medico
    clinicas = medico.clinicas.all()
    escolhas = tuple([(c.id, c.nome_clinica) for c in clinicas])
    paciente_existe = request.session['paciente_existe']
     
    
    if request.method == 'POST':
        formulario = NovoProcesso(escolhas, request.POST)    
            
        if formulario.is_valid():   
            dados_formulario = formulario.cleaned_data
            id_clin = dados_formulario['clinicas']
            clinica = medico.clinicas.get(id=id_clin)

            dados = vincula_dados_emissor(medico,clinica,dados_formulario)

            # Jeitinho, ainda não existem dados condicionais
            dados_condicionais = {}

            formulario.save(usuario)

            path_pdf_final = transfere_dados_gerador(dados,dados_condicionais)
            return redirect(path_pdf_final)
    else:
        if paciente_existe:
            paciente_id = request.session['paciente_id']
            paciente = Paciente.objects.get(id=paciente_id)
            dados_paciente = model_to_dict(paciente)
            formulario = NovoProcesso(escolhas, initial=dados_paciente)
            contexto = {'formulario': formulario, 
                        'paciente_existe': paciente_existe,
                        'paciente': paciente}
        else:
            dados_iniciais = {'cpf_paciente': request.session['cpf_paciente'],
                              'cid': request.session['cid']
                             }         
            formulario = NovoProcesso(escolhas, initial=dados_iniciais)
            contexto = {'formulario': formulario,
                        'paciente_existe': paciente_existe}  

    return render(request, 'processos/cadastro.html', contexto)