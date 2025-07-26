"""
Session Views - Session management and AJAX utilities

This module contains views for session management with simplified control flow.
"""

import json
import logging
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from processos.models import Processo

logger = logging.getLogger(__name__)


@login_required
@csrf_exempt
def set_edit_session(request):
    """Set processo_id in session for editing with simplified control flow."""
    
    # Only handle POST requests
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    # Parse JSON data
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    # Validate required data
    processo_id = data.get('processo_id')
    if not processo_id:
        return JsonResponse({'error': 'processo_id is required'}, status=400)
    
    # Verify user owns this process
    try:
        processo = Processo.objects.get(id=processo_id, usuario=request.user)
    except Processo.DoesNotExist:
        logger.warning(f"Process {processo_id} not found for user {request.user}")
        return JsonResponse({'error': 'Process not found'}, status=404)
    except Exception as e:
        logger.error(f"Error validating process ownership: {e}")
        return JsonResponse({'error': 'Server error'}, status=500)
    
    # Set session data and return success
    try:
        request.session["processo_id"] = str(processo_id)
        request.session["cid"] = processo.doenca.cid
        logger.info(f"Set edit session for processo {processo_id}, user {request.user}")
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"Error setting session data: {e}")
        return JsonResponse({'error': 'Server error'}, status=500)