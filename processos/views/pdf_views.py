"""
PDF Views - PDF display and serving functionality

This module contains views related to PDF operations with simplified control flow:
- pdf: Displays generated PDF links
- serve_pdf: Securely serves PDF files with authorization
"""

import os
import logging
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from analytics.models import PDFGenerationLog
from processos.services.pdf_authorization_service import PDFAuthorizationService

logger = logging.getLogger(__name__)


@login_required
def pdf(request):
    """Displays the generated PDF with simplified control flow."""
    # Only handle GET requests
    if request.method != "GET":
        raise Http404("Method not allowed")
    
    link_pdf = request.session.get("path_pdf_final")
    if not link_pdf:
        raise Http404("PDF link not found in session")
    
    contexto = {"link_pdf": link_pdf}
    return render(request, "processos/pdf.html", contexto)


@login_required
def serve_pdf(request, filename):
    """Serves PDF files securely with simplified control flow and early returns."""
    
    # Step 1: Authorize access (raises Http404 if unauthorized)
    auth_service = PDFAuthorizationService()
    is_authorized, cpf_paciente = auth_service.authorize_pdf_access(request.user, filename)
    
    # Step 2: Check file exists
    tmp_pdf_path = f"/tmp/{filename}"
    if not os.path.exists(tmp_pdf_path):
        logger.warning(f"PDF not found in filesystem: {tmp_pdf_path}")
        raise Http404("PDF not found or expired")
    
    # Step 3: Read and serve file
    try:
        with open(tmp_pdf_path, 'rb') as f:
            pdf_content = f.read()
    except Exception as e:
        logger.error(f"Error reading PDF file {tmp_pdf_path}: {e}")
        raise Http404("Error reading PDF")
    
    # Step 4: Create response with security headers
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    response['X-Content-Type-Options'] = 'nosniff'
    response['X-Frame-Options'] = 'SAMEORIGIN'
    
    # Step 5: Log success and track analytics
    logger.info(f"Successfully served PDF {filename} to user {request.user.email}")
    _track_pdf_analytics(request, pdf_content)
    
    return response


def _track_pdf_analytics(request, pdf_content):
    """Track PDF serving analytics with error handling."""
    try:
        PDFGenerationLog.objects.create(
            user=request.user,
            pdf_type='served',
            success=True,
            generation_time_ms=0,  # No generation time for serving
            file_size_bytes=len(pdf_content),
            ip_address=request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0] if request.META.get('HTTP_X_FORWARDED_FOR') else request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            error_message=''
        )
    except Exception as analytics_error:
        logger.error(f"Error tracking PDF serving analytics: {analytics_error}")