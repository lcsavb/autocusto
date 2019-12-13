from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from medicos.models import Medico
from .forms import NovoProcesso

@login_required
def cadastro(request):
    medico = request.user

    
    if request.method == 'POST':
        formulario = NovoProcesso(request.POST)
        print(request.POST)
    
        if formulario.is_valid(): 
            print(formulario.cleaned_data)
            formulario.save(medico.pk)
    else:
        formulario = NovoProcesso()
    

    return render(request, 'processos/cadastro.html', {'formulario': formulario})