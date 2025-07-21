"""
PDFLayerService Migration Example - Single Service Approach

This shows exactly how to migrate from current functions to a single PDFLayerService class.
Your tests are already prepared for this migration!
"""

from datetime import datetime, timedelta
from typing import List
from io import BytesIO
from django.http import HttpResponse
import logging

from processos.models import Protocolo
from processos.pdf_strategies import DataDrivenStrategy

# FUTURE IMPLEMENTATION EXAMPLE:
class PDFLayerService:
    """
    Single service handling all PDF operations for medical prescriptions.
    
    This replaces all scattered PDF functions with a clean, single interface.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    # PUBLIC API - Main entry points
    def generate_prescription_pdf(self, lme_data: dict, path_lme_base: str) -> HttpResponse:
        """
        Main entry point for PDF generation - replaces GeradorPDF.generico_stream()
        
        MIGRATION FROM: GeradorPDF(data, path).generico_stream(data, path)
        MIGRATION TO:   PDFLayerService().generate_prescription_pdf(data, path)
        """
        try:
            self.logger.info(f"Generating PDF for patient CPF: {lme_data.get('cpf_paciente')}")
            
            # Step 1: Format and prepare data
            formatted_data = self._format_data(lme_data)
            
            # Step 2: Get required templates based on protocol
            protocolo = Protocolo.objects.get(doenca__cid=lme_data['cid'])
            templates = self._get_required_templates(protocolo, formatted_data)
            
            # Step 3: Fill all PDF templates
            filled_pdfs = self._fill_forms_in_memory(templates, formatted_data)
            
            if not filled_pdfs:
                return HttpResponse("PDF generation failed", status=500)
            
            # Step 4: Concatenate into final PDF
            final_pdf_bytes = self._concatenate_pdfs(filled_pdfs)
            
            if not final_pdf_bytes:
                return HttpResponse("PDF concatenation failed", status=500)
            
            # Step 5: Create HTTP response
            return self._create_pdf_response(final_pdf_bytes, lme_data)
            
        except Exception as e:
            self.logger.error(f"PDF generation failed: {e}")
            return HttpResponse("PDF generation failed", status=500)
    
    # PRIVATE METHODS - Internal operations
    def _format_data(self, lme_data: dict) -> dict:
        """
        Format and prepare data for PDF generation.
        
        MIGRATION FROM: formatacao_data(data) + ajustar_campo_18(data) 
        MIGRATION TO:   self._format_data(data)
        
        Combines date formatting and privacy field adjustment.
        """
        # Format prescription dates (from formatacao_data)
        if 'data_1' in lme_data:
            self._format_prescription_dates(lme_data)
            
        # Adjust privacy fields (from ajustar_campo_18)
        self._adjust_privacy_fields(lme_data)
        
        return lme_data
    
    def _fill_forms_in_memory(self, templates: List[str], data: dict) -> List[BytesIO]:
        """
        Fill PDF forms in memory using tmpfs approach.
        
        MIGRATION FROM: preencher_formularios_memory(templates, data)
        MIGRATION TO:   self._fill_forms_in_memory(templates, data)
        """
        import os
        import time
        import pypdftk
        
        filled_pdfs = []
        
        for i, template_path in enumerate(templates):
            if not os.path.exists(template_path):
                self.logger.warning(f"Template not found: {template_path}")
                continue
                
            try:
                # Use tmpfs (RAM filesystem) for performance
                ram_pdf_path = f"/dev/shm/pdf_temp_{os.getpid()}_{i}_{int(time.time())}.pdf"
                
                filled_pdf_path = pypdftk.fill_form(template_path, data, ram_pdf_path)
                
                if filled_pdf_path and os.path.exists(filled_pdf_path):
                    with open(filled_pdf_path, 'rb') as pdf_file:
                        pdf_bytes = pdf_file.read()
                    
                    os.unlink(filled_pdf_path)  # Cleanup
                    
                    if pdf_bytes and pdf_bytes.startswith(b'%PDF-'):
                        filled_pdfs.append(BytesIO(pdf_bytes))
                        
            except Exception as e:
                self.logger.error(f"Failed to fill form {template_path}: {e}")
                continue
        
        return filled_pdfs
    
    def _concatenate_pdfs(self, pdf_streams: List[BytesIO]) -> bytes:
        """
        Concatenate multiple PDFs into single document.
        
        MIGRATION FROM: concatenar_pdfs_memory(pdf_streams)
        MIGRATION TO:   self._concatenate_pdfs(pdf_streams)
        """
        import os
        import time
        import pypdftk
        
        if not pdf_streams:
            return None
            
        if len(pdf_streams) == 1:
            pdf_streams[0].seek(0)
            return pdf_streams[0].read()
        
        try:
            # Create temporary files in RAM
            temp_files = []
            for i, pdf_stream in enumerate(pdf_streams):
                ram_file_path = f"/dev/shm/concat_temp_{os.getpid()}_{i}_{int(time.time())}.pdf"
                
                pdf_stream.seek(0)
                with open(ram_file_path, 'wb') as ram_file:
                    ram_file.write(pdf_stream.read())
                    
                temp_files.append(ram_file_path)
            
            # Concatenate using pypdftk
            output_path = f"/dev/shm/concat_output_{os.getpid()}_{int(time.time())}.pdf"
            concatenated_pdf = pypdftk.concat(temp_files, output_path)
            
            if concatenated_pdf and os.path.exists(concatenated_pdf):
                with open(concatenated_pdf, 'rb') as output_file:
                    pdf_bytes = output_file.read()
                
                # Cleanup
                os.unlink(concatenated_pdf)
                for temp_file in temp_files:
                    try:
                        os.unlink(temp_file)
                    except:
                        pass
                
                return pdf_bytes
                
        except Exception as e:
            self.logger.error(f"PDF concatenation failed: {e}")
            return None
    
    def _get_required_templates(self, protocolo: Protocolo, lme_data: dict) -> List[str]:
        """
        Determine which PDF templates are needed for this prescription.
        
        NEW FUNCTIONALITY - consolidates template selection logic
        """
        templates = [settings.PATH_LME_BASE]  # Always include base LME
        
        # Add disease-specific templates
        strategy = DataDrivenStrategy(protocolo)
        disease_templates = strategy.get_disease_specific_paths(lme_data)
        templates.extend(disease_templates)
        
        # Add medication-specific templates
        med_templates = strategy.get_medication_specific_paths(lme_data)
        templates.extend(med_templates)
        
        # Add conditional templates
        if lme_data.get('consentimento') in ['True', True]:
            consent_path = os.path.join(settings.PATH_PDF_DIR, protocolo.nome, "consentimento.pdf")
            if os.path.exists(consent_path):
                templates.append(consent_path)
        
        if lme_data.get('relatorio') and str(lme_data['relatorio']).strip().lower() != 'false':
            if os.path.exists(settings.PATH_RELATORIO):
                templates.append(settings.PATH_RELATORIO)
        
        if lme_data.get('exames') and str(lme_data['exames']).strip().lower() != 'false':
            if os.path.exists(settings.PATH_EXAMES):
                templates.append(settings.PATH_EXAMES)
        
        return templates
    
    def _format_prescription_dates(self, data: dict) -> None:
        """Format sequential prescription dates (30 days apart)"""
        if 'data_1' not in data:
            return
            
        initial_date = data['data_1']
        days = 30
        
        for month in range(2, 7):  # data_2 through data_6
            new_date = initial_date + timedelta(days=days)
            data[f"data_{month}"] = new_date.strftime("%d/%m/%Y")
            days += 30
            
        # Format original date
        data['data_1'] = initial_date.strftime("%d/%m/%Y")
    
    def _adjust_privacy_fields(self, data: dict) -> None:
        """Remove sensitive fields when not filled by doctor"""
        if data.get("preenchido_por") != "medico":
            sensitive_fields = ["cpf_paciente", "telefone1_paciente", "telefone2_paciente", "email_paciente"]
            for field in sensitive_fields:
                data.pop(field, None)
            data["etnia"] = ""
            data["escolha_documento"] = ""
    
    def _create_pdf_response(self, pdf_bytes: bytes, lme_data: dict) -> HttpResponse:
        """Create HTTP response for PDF download"""
        cpf = lme_data.get('cpf_paciente', 'unknown')
        cid = lme_data.get('cid', 'unknown')
        filename = f"pdf_final_{cpf}_{cid}.pdf"
        
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response


# EXAMPLE USAGE IN VIEWS:
"""
# BEFORE (current):
def generate_pdf_view(request):
    gerador = GeradorPDF(dados_lme_base, path_lme_base)
    return gerador.generico_stream(dados_lme_base, path_lme_base)

# AFTER (with service):
def generate_pdf_view(request):
    pdf_service = PDFLayerService()
    return pdf_service.generate_prescription_pdf(dados_lme_base, path_lme_base)
"""

# TEST MIGRATION EXAMPLE:
"""
# BEFORE (current test):
class TestPDFGeneration(TestCase):
    def test_fill_forms_success(self):
        result = preencher_formularios_memory([template], data)
        self.assertIsInstance(result, list)

# AFTER (service test):
class TestPDFLayerService(TestCase):
    def setUp(self):
        self.service = PDFLayerService()
    
    def test_fill_forms_in_memory_success(self):
        result = self.service._fill_forms_in_memory([template], data)
        self.assertIsInstance(result, list)
        
    def test_generate_prescription_pdf_complete_workflow(self):
        # New integration test for complete workflow
        response = self.service.generate_prescription_pdf(lme_data, template_path)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 200)
"""