from django.shortcuts import render
from processos.forms import PreProcesso

def home(request):
    formulario = PreProcesso()

    contexto = {'formulario': formulario}

    return render(request, 'home.html', contexto)