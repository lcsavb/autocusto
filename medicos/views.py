
from django.shortcuts import render, redirect
from .forms import MedicoCadastroFormulario
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

@transaction.atomic
def cadastro(request):
    if (request.method == 'POST'):
        form = MedicoCadastroFormulario(request.POST)
        if form.is_valid():
            form.save()
            name = form.cleaned_data.get('nome')
            messages.success(request, f'Conta médica criada para {name}! Você já pode fazer o login.')
            return redirect('login')
    else:
        try:
            accepted_invitation = request.session['convite_aceito']
            if accepted_invitation:
                messages.success(request, f'Código aceito, prossiga com o cadastro')
                form = MedicoCadastroFormulario()
                return render(request, 'medicos/cadastro.html', {'formulario': form, 'titulo': 'Cadastro Médico'})
        except:
            return redirect('home')

@login_required
def perfil(request):
    return render(request, 'medicos/perfil.html')
