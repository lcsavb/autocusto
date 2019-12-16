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
from .forms import NovoProcesso
import os
import pypdftk
from .manejo_pdfs import GeradorPDF, gerar_dados_renovacao

class ResultadosBuscaPacientes(LoginRequiredMixin, ListView):
    model = Paciente
    template_name = 'processos/busca.html'
    login_url = '/login/'
    raise_exception = True

    def get_queryset(self):
        
        busca = self.request.GET.get('b')
        object_list = Paciente.objects.filter(
            (Q(nome__icontains=busca) | Q(cpf_paciente__icontains=busca)) 
            & Q(usuario_id__in=Usuario.objects.filter(medico=self.request.user.pk))
        )
        return object_list


@login_required
def renovacao_rapida(request):
    if request.method == 'GET':
        busca = request.GET.get('b')
        usuario = request.user.pk
        pacientes = Paciente.objects.filter(
                (Q(nome__icontains=busca) | 
                Q(cpf_paciente__icontains=busca)) 
                & Q(usuario_id__in=Usuario.objects.filter(id=usuario))
            )

        contexto = {'pacientes': pacientes}
        return render(request, 'processos/renovacao_rapida.html', contexto)

    else: 
        paciente_id = request.POST.get('paciente_id')
        nova_data = request.POST.get('data1')
        cid = request.POST.get('cid')

        dados = gerar_dados_renovacao(nova_data,paciente_id,cid)
        print('na view')
        print(dados)

        
        args = [dados, {}, settings.PATH_LME_BASE]
        pdf = GeradorPDF(*args)
        dados_pdf = pdf.generico(dados,settings.PATH_LME_BASE)
        path_pdf_final = dados_pdf[1] # a segunda variável que a função retorna é o path
        print(path_pdf_final)
        return render(request, 'processos/renovacao_rapida.html')
        

@login_required
def cadastro(request):
    medico = request.user.medico
    usuario = request.user
    
    if request.method == 'POST':
        formulario = NovoProcesso(request.POST)
            
        if formulario.is_valid(): 
            dados = formulario.cleaned_data

            # Registra os dados do médico logado
            dados_medico = {'nome_medico': medico.nome, 'cns_medico': medico.cns}
            dados.update(dados_medico)

            # Jeitinho, ainda não existem dados condicionais
            dados_condicionais = {}

            formulario.save(usuario)
            args = [dados, dados_condicionais, settings.PATH_LME_BASE]
            pdf = GeradorPDF(*args)
            dados_pdf = pdf.generico(dados,settings.PATH_LME_BASE)
            path_pdf_final = dados_pdf[1] # a segunda variável que a função retorna é o path
            return redirect(path_pdf_final)
    else:
        formulario = NovoProcesso()  

    return render(request, 'processos/cadastro.html', {'formulario': formulario})