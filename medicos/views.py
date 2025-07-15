from django.shortcuts import render, redirect
from .forms import MedicoCadastroFormulario
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login


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


@csrf_protect
@require_http_methods(["POST"])
def custom_login(request):
    
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '').strip()
    
    # Check for blank fields
    if not username or not password:
        messages.error(request, "Por favor, preencha todos os campos.")
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    # Try to authenticate
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        messages.success(request, "Login realizado com sucesso!")
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    else:
        messages.error(request, "Email ou senha incorretos.")
        return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def perfil(request):
    return render(request, "medicos/perfil.html")
