from django.shortcuts import render, redirect
from .forms import MedicoCadastroFormulario
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction


@transaction.atomic
def cadastro(request):
    if request.method == "POST":
        formulario = MedicoCadastroFormulario(request.POST)
        if formulario.is_valid():
            formulario.save()
            nome = formulario.cleaned_data.get("nome")
            messages.success(
                request, f"Conta médica criada para {nome}! Você já pode fazer o login."
            )
            return redirect("login")
        else:
            # Add form errors to messages for display
            for field, errors in formulario.errors.items():
                for error in errors:
                    messages.error(request, error)
            # If this came from home page, redirect back with errors
            referer = request.META.get('HTTP_REFERER', '')
            if referer and 'cadastro' not in referer:
                return redirect("home")
    else:
        formulario = MedicoCadastroFormulario()
    
    return render(
        request,
        "medicos/cadastro.html",
        {"formulario": formulario, "titulo": "Cadastro Médico"},
    )


@login_required
def perfil(request):
    return render(request, "medicos/perfil.html")
