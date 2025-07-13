from django.shortcuts import render, redirect
from .forms import PacienteCadastroFormulario
from django.views.generic import ListView
from pacientes.models import Paciente
from django.urls import reverse
from urllib.parse import urlencode


def cadastro(request):

    if request.method == "POST":
        formulario = PacienteCadastroFormulario(request.POST)
        if formulario.is_valid():
            instance = formulario.save(commit=False)
            instance.medico = request.user.medico
            instance.paciente = formulario.cleaned_data["cpf_paciente"]
            url_base = reverse("processos-cadastro")
            string_busca = urlencode({"paciente": instance.paciente})
            url = f"{url_base}?{string_busca}"
            instance.save()

            # nome = formulario.cleaned_data.get('nome')
            # messages.success(request, f'Paciente {nome} adicionado! Agora preencha o processo:')
            return redirect(url)
    else:
        formulario = PacienteCadastroFormulario()

    return render(
        request,
        "pacientes/cadastro.html",
        {"formulario": formulario, "titulo": "Cadastro de Paciente"},
    )


class ListarPacientes(ListView):
    model = Paciente
    template_name = "pacientes/lista.html"
    context_object_name = "pacientes"
