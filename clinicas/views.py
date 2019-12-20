from django.shortcuts import render
from django.db import transaction
from django.contrib.auth.decorators import login_required
from .forms import ClinicaFormulario
from medicos.models import Medico

@login_required
@transaction.atomic
def cadastro(request):
    usuario = request.user
    medico = usuario.medico


    if request.method == 'POST':
        f_clinica = ClinicaFormulario(request.POST)
        
        if f_clinica.is_valid():
            instance = f_clinica.save(commit=False)
            instance.usuario = usuario
            instance.save()
            instance.medicos.add(medico)         
    else:
        f_clinica = ClinicaFormulario()

    contexto = {'f_clinica': f_clinica}

    return render(request, 'clinicas/cadastro.html', contexto)