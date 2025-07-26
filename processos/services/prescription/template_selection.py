"""
Prescription Template Selection Service

Selects appropriate PDF templates based on medical protocols and prescription context.
Contains business logic for disease protocol-based template selection and optional medical documents.

Extracted from prescription_services.py to follow single responsibility principle.
"""

import os
import logging
from typing import List
from django.conf import settings

from processos.models import Protocolo
from processos.services.pdf_strategies import DataDrivenStrategy


class PrescriptionTemplateSelector:
    """
    Selects appropriate PDF templates based on medical protocols and prescription context.
    
    Contains business logic for:
    - Disease protocol-based template selection
    - Medication-specific form selection
    - Optional medical document inclusion (consent, reports, exams)
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def select_prescription_templates(self, protocolo: Protocolo, form_data: dict, base_template: str) -> List[str]:
        """
        Select all required PDF templates for the medical prescription.
        
        Args:
            protocolo: Disease protocol from database
            form_data: Form data containing prescription details
            base_template: Path to base LME template
            
        Returns:
            List[str]: Ordered list of PDF file paths to be filled
        """
        self.logger.debug(f"PrescriptionTemplateSelector: Starting template selection for protocol: {protocolo.nome}")
        self.logger.debug(f"PrescriptionTemplateSelector: Base template: {base_template}")
        
        pdf_file_paths = [base_template]  # Always include base prescription
        
        # Add disease and medication specific PDF files
        protocol_pdfs = self._get_protocol_specific_templates(protocolo, form_data)
        pdf_file_paths.extend(protocol_pdfs)
        self.logger.debug(f"PrescriptionTemplateSelector: Added {len(protocol_pdfs)} protocol-specific PDFs")
        
        # Add optional medical documents
        optional_pdfs = self._get_optional_medical_documents(protocolo, form_data)
        pdf_file_paths.extend(optional_pdfs)
        self.logger.debug(f"PrescriptionTemplateSelector: Added {len(optional_pdfs)} optional medical documents")
        
        self.logger.info(f"PrescriptionTemplateSelector: Total PDF files selected: {len(pdf_file_paths)}")
        for i, pdf_path in enumerate(pdf_file_paths):
            self.logger.debug(f"PrescriptionTemplateSelector: PDF {i+1}: {pdf_path}")
        
        return pdf_file_paths
    
    def _get_protocol_specific_templates(self, protocolo: Protocolo, form_data: dict) -> List[str]:
        """Get disease and medication specific PDF templates."""
        pdf_files = []
        
        try:
            self.logger.debug(f"PrescriptionTemplateSelector: Creating DataDrivenStrategy for protocol: {protocolo.nome}")
            strategy = DataDrivenStrategy(protocolo)
            
            # Disease-specific PDF files
            disease_pdf_paths = strategy.get_disease_specific_paths(form_data)
            if disease_pdf_paths:
                pdf_files.extend(disease_pdf_paths)
                self.logger.debug(f"PrescriptionTemplateSelector: Found {len(disease_pdf_paths)} disease-specific PDFs")
                for pdf in disease_pdf_paths:
                    self.logger.debug(f"PrescriptionTemplateSelector: - Disease PDF: {pdf}")
            
            # Medication-specific PDF files
            med_pdf_paths = strategy.get_medication_specific_paths(form_data)
            if med_pdf_paths:
                pdf_files.extend(med_pdf_paths)
                self.logger.debug(f"PrescriptionTemplateSelector: Found {len(med_pdf_paths)} medication-specific PDFs")
                for pdf in med_pdf_paths:
                    self.logger.debug(f"PrescriptionTemplateSelector: - Medication PDF: {pdf}")
                
        except Exception as e:
            self.logger.error(f"PrescriptionTemplateSelector: Error getting protocol PDFs: {e}", exc_info=True)
        
        return pdf_files
    
    def _get_optional_medical_documents(self, protocolo: Protocolo, form_data: dict) -> List[str]:
        """Get optional medical documents based on prescription requirements."""
        pdf_files = []
        
        # Patient consent form
        consent_value = form_data.get('consentimento')
        self.logger.debug(f"PrescriptionTemplateSelector: Consent value: {consent_value} (type: {type(consent_value)})")
        
        if consent_value in ['True', True, 'true', '1', 1]:
            consent_path = os.path.join(
                settings.PATH_PDF_DIR,
                protocolo.nome,
                "consentimento.pdf"
            )
            self.logger.debug(f"PrescriptionTemplateSelector: Checking consent PDF at: {consent_path}")
            
            if os.path.exists(consent_path):
                pdf_files.append(consent_path)
                self.logger.debug(f"PrescriptionTemplateSelector: Added consent PDF: {consent_path}")
            else:
                self.logger.warning(f"PrescriptionTemplateSelector: Consent PDF not found at: {consent_path}")
        
        # Medical report - check emitir_relatorio flag
        emitir_relatorio = form_data.get('emitir_relatorio')
        relatorio_content = form_data.get('relatorio', '')
        self.logger.debug(f"PrescriptionTemplateSelector: Emitir relatorio: {emitir_relatorio}, content length: {len(str(relatorio_content))}")
        
        if emitir_relatorio in ['True', True, 'true', '1', 1] and relatorio_content and str(relatorio_content).strip():
            if hasattr(settings, 'PATH_RELATORIO'):
                self.logger.debug(f"PrescriptionTemplateSelector: Checking report PDF at: {settings.PATH_RELATORIO}")
                if os.path.exists(settings.PATH_RELATORIO):
                    pdf_files.append(settings.PATH_RELATORIO)
                    self.logger.debug(f"PrescriptionTemplateSelector: Added report PDF: {settings.PATH_RELATORIO}")
                else:
                    self.logger.warning(f"PrescriptionTemplateSelector: Report PDF not found at: {settings.PATH_RELATORIO}")
            else:
                self.logger.warning("PrescriptionTemplateSelector: PATH_RELATORIO not configured in settings")
        
        # Exam request - check emitir_exames flag
        emitir_exames = form_data.get('emitir_exames')
        exames_content = form_data.get('exames', '')
        self.logger.debug(f"PrescriptionTemplateSelector: Emitir exames: {emitir_exames}, content length: {len(str(exames_content))}")
        
        if emitir_exames in ['True', True, 'true', '1', 1] and exames_content and str(exames_content).strip():
            if hasattr(settings, 'PATH_EXAMES'):
                self.logger.debug(f"PrescriptionTemplateSelector: Checking exam PDF at: {settings.PATH_EXAMES}")
                if os.path.exists(settings.PATH_EXAMES):
                    pdf_files.append(settings.PATH_EXAMES)
                    self.logger.debug(f"PrescriptionTemplateSelector: Added exam PDF: {settings.PATH_EXAMES}")
                else:
                    self.logger.warning(f"PrescriptionTemplateSelector: Exam PDF not found at: {settings.PATH_EXAMES}")
            else:
                self.logger.warning("PrescriptionTemplateSelector: PATH_EXAMES not configured in settings")
        
        return pdf_files