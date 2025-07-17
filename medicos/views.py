from django.shortcuts import render, redirect
from .forms import MedicoCadastroFormulario
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout


# English: registration
@transaction.atomic
def cadastro(request):
    """Handles the registration of new medical accounts.

    This view processes the form submission for creating a new doctor's account.
    If the form is valid, it saves the new user and redirects to the login page.
    Otherwise, it displays error messages.

    Critique:
    - The error handling for form validation iterates through `formulario.errors.items()`
      and adds each error as a separate message. While functional, Django's form
      rendering often handles displaying field-specific errors directly in the template,
      making these `messages.error` calls potentially redundant or leading to duplicate
      error displays.
    - The `referer` logic to redirect back to 'home' if not coming from 'cadastro'
      might be overly complex. A simpler approach could be to always redirect to a
      specific success/failure page or to re-render the form with errors.

    Args:
        request: The HTTP request.

    Returns:
        A rendered HTML page or a redirect.
    """
    if request.method == "POST":
        # English: form
        formulario = MedicoCadastroFormulario(request.POST)
        if formulario.is_valid():
            formulario.save()
            # English: name
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
            # English: referer
            referer = request.META.get('HTTP_REFERER', '')
            if referer and 'cadastro' not in referer:
                return redirect("home")
    else:
        # English: form
        formulario = MedicoCadastroFormulario()
    
    return render(
        request,
        "medicos/cadastro.html",
        {"formulario": formulario, "titulo": "Cadastro Médico"},
    )


# English: custom_login
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
    
    # English: username
    username = request.POST.get('username', '').strip()
    # English: password
    password = request.POST.get('password', '').strip()
    
    # Pre-authentication validation to provide immediate feedback
    if not username or not password:
        messages.error(request, "Por favor, preencha todos os campos.")
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    # Attempt authentication using Django's built-in authentication system
    # English: user
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


# English: profile
@login_required
def perfil(request):
    return render(request, "medicos/perfil.html")


def custom_logout(request):
    """Custom logout view that adds success message and redirects to home"""
    logout(request)
    messages.success(request, "Logout realizado com sucesso!")
    return redirect("home")
