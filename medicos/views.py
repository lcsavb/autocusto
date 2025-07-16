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
    """
    Custom login view that handles AJAX-style login from the home page.
    
    This view differs from Django's standard login view in several ways:
    1. It's designed to work with AJAX requests from the home page
    2. Uses HTTP_REFERER to redirect back to the originating page
    3. Provides immediate feedback through Django messages
    4. Handles authentication without full page reloads
    
    The implementation ensures smooth UX for the home page dual-interface
    (registration/login for visitors, process forms for authenticated users).
    """
    
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '').strip()
    
    # Pre-authentication validation to provide immediate feedback
    if not username or not password:
        messages.error(request, "Por favor, preencha todos os campos.")
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    # Attempt authentication using Django's built-in authentication system
    user = authenticate(request, username=username, password=password)
    if user is not None:
        # Authentication successful - establish session
        login(request, user)
        messages.success(request, "Login realizado com sucesso!")
        # Redirect back to originating page (usually home) to show authenticated interface
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    else:
        # Authentication failed - provide user feedback
        messages.error(request, "Email ou senha incorretos.")
        return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def perfil(request):
    return render(request, "medicos/perfil.html")
