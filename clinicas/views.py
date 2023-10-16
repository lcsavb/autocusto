
from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ClinicaFormulario
from medicos.models import Medico
from medicos.seletor import medico as seletor_medico
from clinicas.models import Clinica

@login_required
@transaction.atomic
def cadastro(request):
    usuario = request.user
    medico = seletor_medico(usuario)
    if (request.method == 'POST'):
        f_clinic = ClinicaFormulario(request.POST)
        if f_clinic.is_valid():
            data = f_clinic.cleaned_data
            clinic_exists = Clinica.objects.filter(cns_clinica__exact=data['cns_clinica'])
            if clinic_exists:
                instance = f_clinic.save(commit=False)
                instance.pk = clinic_exists[0].pk
                instance.save(force_update=True)
                instance.usuarios.add(usuario)
                instance.medicos.add(medico)
                messages.success(request, f"Clínica {data['nome_clinica']} cadastrada com sucesso!")
                return redirect('home')
            else:
                instance = f_clinic.save(commit=False)
                instance.save()
                instance.usuarios.add(usuario)
                instance.medicos.add(medico)
                messages.success(request, f"Clínica {data['nome_clinica']} cadastrada com sucesso!")
                return redirect('home')
    else:
        f_clinic = ClinicaFormulario()
    contexto = {'f_clinica': f_clinic}
    return render(request, 'clinicas/cadastro.html', contexto)
