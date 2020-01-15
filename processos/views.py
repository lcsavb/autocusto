from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.conf import settings
from django.db.models import Q
from medicos.models import Medico
from pacientes.models import Paciente
from processos.models import Processo
from usuarios.models import Usuario
from clinicas.models import Clinica
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
        return Processo.objects.filter(usuario=self.request.user)


@login_required
def edicao(request):
    usuario = request.user
    medico = request.user.medico
    clinicas = medico.clinicas.all()
    escolhas = tuple([(c.id, c.nome_clinica) for c in clinicas])    
    
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

            formulario.save(usuario)

            args = [dados, dados_condicionais, settings.PATH_LME_BASE]
            pdf = GeradorPDF(*args)
            dados_pdf = pdf.generico(dados,settings.PATH_LME_BASE)
            path_pdf_final = dados_pdf[1] # a segunda variável que a função retorna é o path
            return redirect(path_pdf_final)
    else:
        processo_id = request.GET.get('id')
        processo = Processo.objects.get(id=processo_id)
        dados_iniciais = cria_dict_renovação(processo)
        formulario = RenovarProcesso(escolhas, initial=dados_iniciais)

    contexto = {'formulario': formulario, 'processo': processo}  

    return render(request, 'processos/edicao.html', contexto)




@login_required
def renovacao_rapida(request):
    if request.method == 'GET':
        busca = request.GET.get('b')
        pacientes = Paciente.objects.filter(
            Q(processos__usuario=request.user)
            &
            (Q(nome_paciente__icontains=busca) | Q(cpf_paciente__icontains=busca))
        )

        contexto = {'pacientes': pacientes}
        return render(request, 'processos/renovacao_rapida.html', contexto)

    else: 
        processo_id = request.POST.get('processo_id')
        nova_data = request.POST.get('data1')

        dados = gerar_dados_renovacao(nova_data,processo_id)
        
        args = [dados, {}, settings.PATH_LME_BASE]
        pdf = GeradorPDF(*args)
        dados_pdf = pdf.generico(dados,settings.PATH_LME_BASE)
        path_pdf_final = dados_pdf[1] # a segunda variável que a função retorna é o path
        return redirect(path_pdf_final)
        

@login_required
def cadastro(request):
    usuario = request.user
    medico = request.user.medico
    clinicas = medico.clinicas.all()
    escolhas = tuple([(c.id, c.nome_clinica) for c in clinicas])    
    
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
        formulario = NovoProcesso(escolhas)

    contexto = {'formulario': formulario}  

    return render(request, 'processos/cadastro.html', contexto)