from django.shortcuts import render, redirect
from .forms import MedicoCadastroFormulario

def cadastro(request):
    
    if request.method == 'POST':
        formulario = MedicoCadastroFormulario(request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect('home')
    else:
        formulario = MedicoCadastroFormulario()
    
    return render(request, 'medicos/cadastro.html', {'formulario': formulario, 'titulo': 'Cadastro Médico'})