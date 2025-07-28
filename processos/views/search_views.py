"""
Search Views - Process search functionality

This module contains views for searching processes with simplified control flow.
"""

import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from processos.services.view_services import PrescriptionViewSetupService
from processos.services.view_setup_models import SetupError

logger = logging.getLogger(__name__)


@login_required
def busca_processos(request):
    """Searches for processes associated with the logged-in user with simplified control flow."""
    
    if request.method == "GET":
        # Since busca.html template is deprecated, redirect to home
        messages.info(request, "Funcionalidade de busca foi atualizada. Redirecionando para a página inicial.")
        return redirect("home")
    
    # Handle POST request - process selection
    processo_id = request.POST.get("processo_id")
    if not processo_id:
        messages.error(request, "ID do processo é obrigatório")
        return redirect("processos-busca")
    
    # Use service to handle process selection business logic
    setup_service = PrescriptionViewSetupService()
    result = setup_service.setup_process_for_editing(processo_id, request.user, request)
    
    # Handle service result
    if isinstance(result, SetupError):
        messages.error(request, result.message)
        return redirect(result.redirect_to)
    
    # Success - redirect to editing
    success_message = result.specific['success_message']
    redirect_to = result.specific['redirect_to']
    messages.success(request, success_message)
    return redirect(redirect_to)