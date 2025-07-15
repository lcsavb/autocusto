from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ClinicaFormulario
from medicos.seletor import medico as seletor_medico
from clinicas.models import Clinica


@login_required
@transaction.atomic
def cadastro(request):
    usuario = request.user
    medico = seletor_medico(usuario)

    if request.method == "POST":
        f_clinica = ClinicaFormulario(request.POST)

        if f_clinica.is_valid():
            dados = f_clinica.cleaned_data

            clinica_existe = Clinica.objects.filter(
                cns_clinica__exact=dados["cns_clinica"]
            )

            if clinica_existe:
                instance = f_clinica.save(commit=False)
                instance.pk = clinica_existe[0].pk
                instance.save(force_update=True)
                instance.usuarios.add(usuario)
                instance.medicos.add(medico)
                messages.success(
                    request, f'Clínica {dados["nome_clinica"]} cadastrada com sucesso!'
                )
                return redirect("home")
            else:
                instance = f_clinica.save(commit=False)
                instance.save()
                instance.usuarios.add(usuario)
                instance.medicos.add(medico)
                messages.success(
                    request, f'Clínica {dados["nome_clinica"]} cadastrada com sucesso!'
                )
                return redirect("home")
        else:
            # Form validation failed - add errors as Django messages for toast display
            for field, errors in f_clinica.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        f_clinica = ClinicaFormulario()

    contexto = {"f_clinica": f_clinica}

    return render(request, "clinicas/cadastro.html", contexto)
