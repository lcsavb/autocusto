"""
I/O Services for file operations and external system interactions.

This module contains services that handle I/O concerns like
file operations, URL generation, and filesystem interactions,
separate from business logic.
"""

import os
import logging
from django.http import HttpResponse
from django.urls import reverse

pdf_logger = logging.getLogger('processos.pdf')


class PDFFileService:
    """
    Service for PDF file I/O operations.
    
    Handles file operations separate from business logic,
    including saving PDFs to filesystem and generating serving URLs.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def save_pdf_and_get_url(self, pdf_response: HttpResponse, cpf_paciente: str, cid: str) -> str:
        """
        Save PDF response to filesystem and return serving URL.
        
        Args:
            pdf_response: HttpResponse containing PDF content
            cpf_paciente: Patient CPF for filename
            cid: Disease CID for filename
            
        Returns:
            str: URL path for serving the PDF file
            
        Raises:
            Exception: If file save operation fails
        """
        try:
            # Generate filename
            nome_final_pdf = f"pdf_final_{cpf_paciente}_{cid}.pdf"
            tmp_pdf_path = f"/tmp/{nome_final_pdf}"
            
            # Save PDF content to file
            with open(tmp_pdf_path, 'wb') as f:
                f.write(pdf_response.content)
            
            pdf_logger.info(f"PDFFileService: PDF saved to {tmp_pdf_path}")
            
            # Generate serving URL
            path_pdf_final = reverse('processos-serve-pdf', kwargs={'filename': nome_final_pdf})
            
            pdf_logger.info(f"PDFFileService: Generated serving URL: {path_pdf_final}")
            return path_pdf_final
            
        except Exception as e:
            pdf_logger.error(f"PDFFileService: Failed to save PDF: {e}", exc_info=True)
            raise