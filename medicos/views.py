from django.shortcuts import render, redirect
from .forms import MedicoCadastroFormulario
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def cadastro(request):
    
    if request.method == 'POST':
        formulario = MedicoCadastroFormulario(request.POST)
        if formulario.is_valid():
            formulario.save()
            username = formulario.cleaned_data.get('username')
            messages.success(request, f'Conta criada para {nome}! Você já pode fazer o login.')
            return redirect('login')
    else:
        formulario = MedicoCadastroFormulario()
    
    return render(request, 'medicos/cadastro.html', {'formulario': formulario, 'titulo': 'Cadastro Médico'})

@login_required
def perfil(request):
    return render(request, 'medicos/perfil.html')