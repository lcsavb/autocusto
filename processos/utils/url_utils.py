"""
URL Utils - URL Generation Utilities

This module contains pure utility functions for URL generation and manipulation.
These functions are stateless and have no business logic or side effects.

Extracted from helpers.py to follow utility pattern principles.
"""

import os
import logging
from typing import Optional
from django.conf import settings


logger = logging.getLogger(__name__)


def generate_protocol_link(cid: str) -> str:
    """
    Generate a link to the protocol file for a given CID.
    
    This utility function constructs the URL path to the protocol PDF file
    based on the disease CID code.
    
    Args:
        cid: The CID code for the disease
        
    Returns:
        str: The URL to the protocol file
        
    Raises:
        DoesNotExist: If no protocol is found for the CID
    """
    from processos.models import Protocolo
    
    logger.debug(f"URLUtils: Generating protocol link for CID {cid}")
    
    try:
        protocol = Protocolo.objects.get(doenca__cid=cid)
        file_path = protocol.arquivo
        
        # Construct the full URL
        protocol_url = os.path.join(settings.STATIC_URL, "protocolos", file_path)
        
        logger.debug(f"URLUtils: Generated protocol link: {protocol_url}")
        return protocol_url
        
    except Protocolo.DoesNotExist:
        logger.error(f"URLUtils: No protocol found for CID {cid}")
        raise


def generate_pdf_serving_url(filename: str, base_path: str = "serve_pdf") -> str:
    """
    Generate URL for serving PDF files.
    
    This utility constructs URLs for serving generated PDF files through
    the application's PDF serving endpoint.
    
    Args:
        filename: Name of the PDF file to serve
        base_path: Base path for the PDF serving endpoint
        
    Returns:
        str: Complete URL for PDF serving
    """
    from django.urls import reverse
    
    logger.debug(f"URLUtils: Generating PDF serving URL for {filename}")
    
    try:
        pdf_url = reverse(base_path, kwargs={'filename': filename})
        logger.debug(f"URLUtils: Generated PDF URL: {pdf_url}")
        return pdf_url
    except Exception as e:
        logger.error(f"URLUtils: Error generating PDF URL: {e}")
        return f"/{base_path}/{filename}"  # Fallback URL


def build_static_file_url(file_path: str, static_dir: str = "") -> str:
    """
    Build URL for static files.
    
    This utility constructs URLs for static files, handling the static URL
    configuration and path joining properly.
    
    Args:
        file_path: Path to the static file
        static_dir: Optional subdirectory within static files
        
    Returns:
        str: Complete URL to the static file
    """
    logger.debug(f"URLUtils: Building static file URL for {file_path}")
    
    if static_dir:
        full_path = os.path.join(settings.STATIC_URL, static_dir, file_path)
    else:
        full_path = os.path.join(settings.STATIC_URL, file_path)
    
    # Normalize path separators for web URLs
    web_url = full_path.replace(os.path.sep, '/')
    
    logger.debug(f"URLUtils: Built static URL: {web_url}")
    return web_url


def generate_download_filename(patient_cpf: str, cid: str, timestamp: Optional[str] = None) -> str:
    """
    Generate standardized filename for PDF downloads.
    
    This utility creates consistent, secure filenames for PDF downloads
    based on patient and process information.
    
    Args:
        patient_cpf: Patient CPF for filename identification
        cid: Disease CID code
        timestamp: Optional timestamp string
        
    Returns:
        str: Standardized filename for PDF download
    """
    from datetime import datetime
    
    logger.debug(f"URLUtils: Generating download filename for CPF {patient_cpf}, CID {cid}")
    
    # Sanitize CPF (remove dots and dashes)
    clean_cpf = patient_cpf.replace('.', '').replace('-', '')
    
    # Use provided timestamp or generate current one
    if not timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Build filename with consistent format
    filename = f"prescricao_{clean_cpf}_{cid}_{timestamp}.pdf"
    
    logger.debug(f"URLUtils: Generated filename: {filename}")
    return filename


def validate_filename_security(filename: str) -> bool:
    """
    Validate filename for security issues.
    
    This utility checks filenames for potentially dangerous characters
    or patterns that could be used for path traversal attacks.
    
    Args:
        filename: Filename to validate
        
    Returns:
        bool: True if filename is safe, False otherwise
    """
    logger.debug(f"URLUtils: Validating filename security: {filename}")
    
    # Check for path traversal patterns
    dangerous_patterns = ['..', '/', '\\', '~', '$', '&', '|', ';', '`']
    
    for pattern in dangerous_patterns:
        if pattern in filename:
            logger.warning(f"URLUtils: Dangerous pattern '{pattern}' found in filename")
            return False
    
    # Check for acceptable characters (alphanumeric, dots, dashes, underscores)
    allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_')
    if not all(char in allowed_chars for char in filename):
        logger.warning(f"URLUtils: Invalid characters found in filename")
        return False
    
    logger.debug(f"URLUtils: Filename passed security validation")
    return True


def build_api_endpoint_url(endpoint: str, **params) -> str:
    """
    Build URL for API endpoints with parameters.
    
    This utility constructs URLs for internal API calls with proper
    parameter encoding.
    
    Args:
        endpoint: API endpoint name
        **params: URL parameters to include
        
    Returns:
        str: Complete API endpoint URL
    """
    from urllib.parse import urlencode
    
    logger.debug(f"URLUtils: Building API URL for endpoint {endpoint}")
    
    base_url = f"/api/{endpoint}/"
    
    if params:
        query_string = urlencode(params)
        full_url = f"{base_url}?{query_string}"
    else:
        full_url = base_url
    
    logger.debug(f"URLUtils: Built API URL: {full_url}")
    return full_url