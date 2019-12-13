from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings
from medicos.models import Medico
from .forms import NovoProcesso
import os
import pypdftk
from .manejo_pdfs import GeradorPDF

@login_required
def cadastro(request):
    medico = request.user

    
    if request.method == 'POST':
        formulario = NovoProcesso(request.POST)
            
        if formulario.is_valid(): 
            dados = formulario.cleaned_data
            dados_medico = {'nome_medico': medico.nome, 'cns_medico': medico.cns}
            dados.update(dados_medico)
            dados_condicionais = {}
            formulario.save(medico.pk)
            args = [dados, dados_condicionais, settings.PATH_LME_BASE]
            pdf = GeradorPDF(*args)
            dados_pdf = pdf.generico(dados,settings.PATH_LME_BASE)
            path_pdf_final = dados_pdf[1] # a segunda variável que a função retorna é o path
            return redirect(path_pdf_final)
    else:
        formulario = NovoProcesso()


    

    return render(request, 'processos/cadastro.html', {'formulario': formulario})