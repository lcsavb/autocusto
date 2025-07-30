"""
Pure PDF Operations - Infrastructure Layer

This module provides ONLY pure PDF technical operations with no business logic.
It's completely agnostic about medical prescriptions or any domain-specific concepts.

Services:
- PDFGenerator: Core PDF filling and concatenation using pypdftk
- PDFResponseBuilder: Creates HTTP responses for PDF delivery

These services can be used for ANY PDF operations, not just medical prescriptions.
"""

import os
import time
import logging
from typing import List, Optional
from datetime import datetime

import pypdftk
from django.http import HttpResponse


logger = logging.getLogger(__name__)
pdf_logger = logging.getLogger('processos.pdf')


class PDFGenerator:
    """
    Pure PDF technical operations using pypdftk.
    
    Single Responsibility: Generate PDFs from templates and data.
    Completely agnostic about business logic or domain concepts.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pdf_logger = logging.getLogger('processos.pdf')
        self.temp_files = []  # Track temporary files for cleanup
    
    def _cleanup_temp_files(self):
        """
        Clean up all temporary PDF files created during generation.
        
        This method removes temporary files from /dev/shm to prevent
        resource leakage and disk space exhaustion.
        """
        if not self.temp_files:
            return
            
        cleaned_count = 0
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    cleaned_count += 1
                    self.pdf_logger.debug(f"PDFGenerator: Cleaned up temp file: {os.path.basename(temp_file)}")
            except Exception as e:
                self.logger.warning(f"PDFGenerator: Failed to clean up {temp_file}: {e}")
        
        if cleaned_count > 0:
            self.pdf_logger.info(f"PDFGenerator: Cleaned up {cleaned_count} temporary files from /dev/shm")
        
        # Clear the list after cleanup
        self.temp_files.clear()
        
    def fill_and_concatenate(self, template_paths: List[str], form_data: dict) -> Optional[bytes]:
        """
        Fill PDF templates with data and concatenate into single document.
        
        WORKFLOW (pypdftk.concat flattens forms):
        1. Fill each PDF template individually with form data
        2. Concatenate the filled PDFs into final document
        3. Clean up temporary files from /dev/shm
        4. Return the final PDF bytes
        
        Args:
            template_paths: List of PDF template file paths
            form_data: Dictionary of form field data for filling
            
        Returns:
            bytes: Final PDF document, or None if generation fails
        """
        self.pdf_logger.info(f"PDFGenerator: Starting generation with {len(template_paths)} PDF files")
        
        try:
            # Step 1: Fill each PDF template individually
            self.pdf_logger.info("PDFGenerator: Step 1 - Filling individual PDF templates")
            filled_pdf_paths = self._fill_pdf_forms(template_paths, form_data)
            
            if not filled_pdf_paths:
                self.logger.error("PDFGenerator: No PDFs were successfully filled")
                return None
            
            # Step 2: Concatenate the filled PDFs
            self.pdf_logger.info("PDFGenerator: Step 2 - Concatenating filled PDFs")
            final_pdf_bytes = self._concatenate_pdfs(filled_pdf_paths)
            
            if final_pdf_bytes:
                self.pdf_logger.info(f"PDFGenerator: Generation complete, final PDF size: {len(final_pdf_bytes)} bytes")
            else:
                self.logger.error("PDFGenerator: Concatenation failed")
                
            return final_pdf_bytes
            
        finally:
            # Step 3: Always clean up temporary files, even if generation fails
            self._cleanup_temp_files()
    
    def _fill_pdf_forms(self, template_paths: List[str], form_data: dict) -> List[str]:
        """
        Fill PDF forms using tmpfs for memory optimization.
        
        Returns list of paths to filled PDFs in tmpfs.
        """
        filled_pdf_paths = []
        
        for i, template_path in enumerate(template_paths):
            self.pdf_logger.debug(f"PDFGenerator: Processing PDF {i+1}/{len(template_paths)}: {template_path}")
            
            if not os.path.exists(template_path):
                self.logger.warning(f"PDFGenerator: Template not found: {template_path}")
                continue
                
            try:
                # Use tmpfs for memory-based operations
                timestamp = int(time.time() * 1000)
                ram_pdf_path = f"/dev/shm/pdf_temp_{os.getpid()}_{i}_{timestamp}.pdf"
                self.pdf_logger.debug(f"PDFGenerator: Filling to RAM path: {ram_pdf_path}")
                
                # Track temp file for cleanup
                self.temp_files.append(ram_pdf_path)
                
                # Debug: Log form data to identify problematic values
                self.pdf_logger.debug(f"PDFGenerator: Form data keys: {list(form_data.keys())}")
                self.pdf_logger.debug(f"PDFGenerator: Form data sample: {dict(list(form_data.items())[:5])}")
                
                # Check for problematic values that might cause pdftk to fail
                cleaned_form_data = {}
                for key, value in form_data.items():
                    if value is None:
                        cleaned_form_data[key] = ""
                    elif isinstance(value, (list, dict)):
                        # Convert complex types to strings
                        cleaned_form_data[key] = str(value)
                    else:
                        cleaned_form_data[key] = str(value)
                
                # Fill form
                filled_path = pypdftk.fill_form(
                    template_path,
                    cleaned_form_data,
                    ram_pdf_path,
                    flatten=False
                )
                
                if filled_path and os.path.exists(filled_path):
                    # Validate PDF exists and has content
                    file_size = os.path.getsize(filled_path)
                    self.pdf_logger.debug(f"PDFGenerator: Filled PDF size: {file_size} bytes")
                    
                    if file_size > 100:
                        filled_pdf_paths.append(filled_path)
                        self.pdf_logger.info(f"PDFGenerator: Successfully filled: {os.path.basename(template_path)}")
                    else:
                        self.logger.warning(f"PDFGenerator: Filled PDF too small ({file_size} bytes): {filled_path}")
                else:
                    self.logger.warning(f"PDFGenerator: pypdftk returned no output for: {template_path}")
                        
            except Exception as e:
                self.logger.error(f"PDFGenerator: Failed to fill {template_path}: {e}", exc_info=True)
        
        self.pdf_logger.info(f"PDFGenerator: Filled {len(filled_pdf_paths)} out of {len(template_paths)} PDFs")
        return filled_pdf_paths
    
    def _concatenate_pdfs(self, pdf_paths: List[str]) -> Optional[bytes]:
        """Concatenate multiple PDFs into single document."""
        if not pdf_paths:
            self.logger.error("PDFGenerator: No PDFs to concatenate")
            return None
            
        # Single PDF optimization - just read and return
        if len(pdf_paths) == 1:
            try:
                self.pdf_logger.debug(f"PDFGenerator: Single PDF, reading directly: {pdf_paths[0]}")
                with open(pdf_paths[0], 'rb') as f:
                    pdf_bytes = f.read()
                self.pdf_logger.debug(f"PDFGenerator: Read {len(pdf_bytes)} bytes")
                return pdf_bytes
            except Exception as e:
                self.logger.error(f"PDFGenerator: Failed to read single PDF: {e}", exc_info=True)
                return None
        
        try:
            # Concatenate using pypdftk directly with file paths
            output_path = f"/dev/shm/output_{os.getpid()}_{int(time.time() * 1000)}.pdf"
            self.pdf_logger.debug(f"PDFGenerator: Concatenating {len(pdf_paths)} PDFs to: {output_path}")
            
            # Track output file for cleanup
            self.temp_files.append(output_path)
            
            result = pypdftk.concat(pdf_paths, output_path)
            
            if result and os.path.exists(result):
                file_size = os.path.getsize(result)
                self.pdf_logger.debug(f"PDFGenerator: Concatenated PDF size: {file_size} bytes")
                
                with open(result, 'rb') as f:
                    pdf_bytes = f.read()
                
                self.pdf_logger.info(f"PDFGenerator: Successfully concatenated {len(pdf_paths)} PDFs")
                return pdf_bytes
            else:
                self.logger.error("PDFGenerator: pypdftk concat returned no output")
                return None
                
        except Exception as e:
            self.logger.error(f"PDFGenerator: Concatenation failed: {e}", exc_info=True)
            return None


class PDFResponseBuilder:
    """
    Creates HTTP responses for PDF delivery.
    
    Single Responsibility: Build HTTP responses with proper headers.
    Completely agnostic about business logic.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def build_response(self, pdf_bytes: bytes, filename: str) -> HttpResponse:
        """
        Create HTTP response for PDF delivery.
        
        Args:
            pdf_bytes: PDF document data
            filename: Filename for the PDF
            
        Returns:
            HttpResponse: Configured response for PDF delivery
        """
        self.logger.debug(f"PDFResponseBuilder: Building response for file: {filename}")
        
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        response['Content-Length'] = len(pdf_bytes)
        
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'SAMEORIGIN'
        
        self.logger.info(f"PDFResponseBuilder: Created response for {filename} ({len(pdf_bytes)} bytes)")
        return response