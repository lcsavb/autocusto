from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import NovoProcesso

@login_required
def cadastro(request):
    formulario = NovoProcesso(request.POST)
    if request.method == 'POST' and formulario.is_valid():
            print(formulario.cleaned_data)
    else:
        formulario = NovoProcesso()

    return render(request, 'processos/cadastro.html', {'formulario': formulario})