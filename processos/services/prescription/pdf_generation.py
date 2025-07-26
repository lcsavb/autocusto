"""
Prescription PDF Generation Service

Complete prescription PDF generation service orchestrating all business logic.
Coordinates medical data formatting, protocol-based template selection, and pure PDF generation.

Extracted from prescription_services.py to follow single responsibility principle.
"""

import time
import logging
from typing import Optional
from datetime import datetime
from django.http import HttpResponse
from django.conf import settings

from processos.services.pdf_operations import PDFGenerator, PDFResponseBuilder
from processos.models import Protocolo
from .data_formatting import PrescriptionDataFormatter
from .template_selection import PrescriptionTemplateSelector
from analytics.signals import track_pdf_generation


class PrescriptionPDFService:
    """
    Complete prescription PDF generation service orchestrating all business logic.
    
    Coordinates:
    - Medical data formatting
    - Protocol-based template selection  
    - Pure PDF generation
    - Medical prescription validation
    """
    
    def __init__(self):
        self.data_formatter = PrescriptionDataFormatter()
        self.template_selector = PrescriptionTemplateSelector()
        self.pdf_generator = PDFGenerator()
        self.response_builder = PDFResponseBuilder()
        self.logger = logging.getLogger(__name__)
        self.pdf_logger = logging.getLogger('processos.pdf')
    
    @track_pdf_generation(pdf_type='prescription')
    def generate_prescription_pdf(self, prescription_data: dict, user=None) -> Optional[HttpResponse]:
        """
        Generate a medical prescription PDF following Brazilian regulations.
        
        Args:
            prescription_data: Complete prescription data dictionary
            user: User for analytics tracking
            
        Returns:
            HttpResponse: Generated PDF response, or None if generation fails
        """
        try:
            start_time = time.time()
            self.pdf_logger.info("="*80)
            self.pdf_logger.info("PrescriptionPDFService: Starting prescription PDF generation")
            self.pdf_logger.info(f"PrescriptionPDFService: Patient CPF: {prescription_data.get('cpf_paciente', 'N/A')}")
            self.pdf_logger.info(f"PrescriptionPDFService: Disease CID: {prescription_data.get('cid', 'N/A')}")
            
            # Validate prescription data
            if not self._validate_prescription_data(prescription_data):
                self.logger.error("PrescriptionPDFService: Invalid prescription data")
                return None
            
            # Step 1: Format medical data
            self.pdf_logger.info("PrescriptionPDFService: Step 1 - Formatting medical data")
            formatted_data = self.data_formatter.format_prescription_date(prescription_data)
            
            # Step 2: Get medical protocol
            self.pdf_logger.info("PrescriptionPDFService: Step 2 - Getting medical protocol")
            protocolo = self._get_medical_protocol(formatted_data)
            if not protocolo:
                self.logger.error("PrescriptionPDFService: Medical protocol not found")
                return HttpResponse("Medical protocol not found", status=404)
            self.pdf_logger.info(f"PrescriptionPDFService: Found protocol: {protocolo.nome}")
            
            # Step 3: Select prescription templates
            self.pdf_logger.info("PrescriptionPDFService: Step 3 - Selecting prescription templates")
            pdf_file_paths = self.template_selector.select_prescription_templates(
                protocolo, 
                formatted_data, 
                settings.PATH_LME_BASE
            )
            self.pdf_logger.info(f"PrescriptionPDFService: Selected {len(pdf_file_paths)} PDF templates")
            
            # Step 4: Generate PDF
            self.pdf_logger.info("PrescriptionPDFService: Step 4 - Generating PDF")
            pdf_bytes = self.pdf_generator.fill_and_concatenate(pdf_file_paths, formatted_data)
            if not pdf_bytes:
                self.logger.error("PrescriptionPDFService: PDF generation failed")
                return HttpResponse("PDF generation failed", status=500)
            
            # Step 5: Build response
            self.pdf_logger.info("PrescriptionPDFService: Step 5 - Building HTTP response")
            filename = self._generate_prescription_filename(prescription_data)
            response = self.response_builder.build_response(pdf_bytes, filename)
            
            elapsed_time = time.time() - start_time
            self.pdf_logger.info(f"PrescriptionPDFService: PDF generation completed in {elapsed_time:.2f} seconds")
            self.pdf_logger.info("="*80)
            
            return response
            
        except Exception as e:
            self.logger.error(f"PrescriptionPDFService: PDF generation failed with exception: {e}", exc_info=True)
            return HttpResponse("PDF generation error", status=500)
    
    def _validate_prescription_data(self, data: dict) -> bool:
        """Validate prescription data contains required medical fields."""
        required_fields = ['cpf_paciente', 'cid', 'data_1']
        
        for field in required_fields:
            if field not in data or not data[field]:
                self.logger.error(f"PrescriptionPDFService: Missing required field: {field}")
                return False
                
        return True
    
    def _get_medical_protocol(self, data: dict) -> Optional[Protocolo]:
        """Get medical protocol for the disease CID."""
        if 'cid' not in data:
            self.logger.error("PrescriptionPDFService: CID not found in data")
            return None
            
        try:
            cid = data['cid']
            self.logger.debug(f"PrescriptionPDFService: Looking up protocol for CID: {cid}")
            protocolo = Protocolo.objects.get(doenca__cid=cid)
            self.logger.debug(f"PrescriptionPDFService: Found protocol: {protocolo.nome} (ID: {protocolo.id})")
            return protocolo
        except Protocolo.DoesNotExist:
            self.logger.error(f"PrescriptionPDFService: Protocol not found for CID: {data['cid']}")
            return None
        except Exception as e:
            self.logger.error(f"PrescriptionPDFService: Error fetching protocol: {e}", exc_info=True)
            return None
    
    def _generate_prescription_filename(self, data: dict) -> str:
        """Generate meaningful filename for prescription PDF."""
        cpf = data.get('cpf_paciente', 'documento')
        cid = data.get('cid', 'protocolo')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        filename = f"prescricao_{cpf}_{cid}_{timestamp}.pdf"
        self.logger.debug(f"PrescriptionPDFService: Generated filename: {filename}")
        return filename