
from django.shortcuts import render, redirect
from .forms import PacienteCadastroFormulario
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from pacientes.models import Paciente
from django.urls import reverse
from urllib.parse import urlencode

def cadastro(request):
    if (request.method == 'POST'):
        form = PacienteCadastroFormulario(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.medico = request.user.medico
            instance.paciente = form.cleaned_data['cpf_paciente']
            base_url = reverse('processos-cadastro')
            string_busca = urlencode({'paciente': instance.paciente})
            url = f'{base_url}?{string_busca}'
            instance.save()
            return redirect(url)
    else:
        form = PacienteCadastroFormulario()
    return render(request, 'pacientes/cadastro.html', {'formulario': form, 'titulo': 'Cadastro de Paciente'})

class ListarPacientes(ListView):
    model = Paciente
    template_name = 'pacientes/lista.html'
    context_object_name = 'pacientes'
