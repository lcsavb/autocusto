"""
Prescription Services - Business Logic Layer

This module contains all medical prescription business logic for the AutoCusto system.
It handles medical data formatting, protocol-based template selection, and prescription workflows.

Services:
- PrescriptionDataFormatter: Medical data preparation and privacy handling
- PrescriptionTemplateSelector: Medical protocol-based template selection
- PrescriptionPDFService: Complete prescription PDF generation workflow
- PrescriptionService: Full prescription business workflow (database + PDF)
- RenewalService: Prescription renewal business logic

These services contain domain-specific knowledge about medical prescriptions,
Brazilian medical protocols, and healthcare data privacy requirements.
"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

from django.conf import settings
from django.db import transaction
from django.http import HttpResponse

from processos.services.pdf_operations import PDFGenerator, PDFResponseBuilder
from processos.models import Processo, Protocolo, Doenca
from processos.services.pdf_strategies import DataDrivenStrategy
from clinicas.models import Emissor
from analytics.signals import track_pdf_generation


logger = logging.getLogger(__name__)
pdf_logger = logging.getLogger('processos.pdf')


class PrescriptionDataFormatter:
    """
    Handles medical prescription data preparation and formatting.
    
    Contains business logic for:
    - Medical data privacy rules
    - Brazilian prescription date formatting
    - Healthcare data validation
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def format_prescription_data(self, raw_data: dict) -> dict:
        """
        Format medical prescription data according to business rules.
        
        Args:
            raw_data: Unformatted prescription form data
            
        Returns:
            dict: Formatted data ready for PDF filling
        """
        self.logger.debug(f"PrescriptionDataFormatter: Starting format with {len(raw_data)} fields")
        
        # Create a copy to avoid modifying original
        data = raw_data.copy()
        
        # Apply medical data formatting
        self._format_prescription_dates(data)
        self._apply_privacy_rules(data)
        
        self.logger.debug(f"PrescriptionDataFormatter: Formatting complete, {len(data)} fields in output")
        return data
    
    def _format_prescription_dates(self, data: dict) -> None:
        """Generate sequential prescription dates (30 days apart) per Brazilian regulations."""
        self.logger.debug("PrescriptionDataFormatter: Checking for date formatting")
        
        if 'data_1' not in data or not data['data_1']:
            self.logger.debug("PrescriptionDataFormatter: No data_1 found, skipping date formatting")
            return
            
        initial_date = data['data_1']
        self.logger.debug(f"PrescriptionDataFormatter: Initial date type: {type(initial_date)}, value: {initial_date}")
        
        # Ensure initial_date is a datetime object
        if isinstance(initial_date, str):
            try:
                initial_date = datetime.strptime(initial_date, "%d/%m/%Y")
                self.logger.debug(f"PrescriptionDataFormatter: Parsed string date to datetime: {initial_date}")
            except ValueError:
                self.logger.warning(f"PrescriptionDataFormatter: Invalid date format: {initial_date}")
                return
        
        # Generate sequential dates for 6-month prescription
        for month in range(1, 7):
            date_obj = initial_date + timedelta(days=30 * (month - 1))
            formatted_date = date_obj.strftime("%d/%m/%Y")
            data[f"data_{month}"] = formatted_date
            self.logger.debug(f"PrescriptionDataFormatter: Set data_{month} = {formatted_date}")
    
    def _apply_privacy_rules(self, data: dict) -> None:
        """Apply Brazilian healthcare privacy rules based on who filled the form."""
        filled_by = data.get("preenchido_por")
        self.logger.debug(f"PrescriptionDataFormatter: Form filled by: {filled_by}")
        
        if filled_by != "medico":
            # Remove sensitive patient data when not filled by doctor
            sensitive_fields = [
                "cpf_paciente",
                "telefone1_paciente", 
                "telefone2_paciente",
                "email_paciente"
            ]
            
            removed_fields = []
            for field in sensitive_fields:
                if field in data:
                    data.pop(field, None)
                    removed_fields.append(field)
            
            # Clear additional sensitive fields
            data["etnia"] = ""
            data["escolha_documento"] = ""
            
            self.logger.debug(f"PrescriptionDataFormatter: Removed sensitive fields: {removed_fields}")


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
            formatted_data = self.data_formatter.format_prescription_data(prescription_data)
            
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


class PrescriptionService:
    """
    Complete prescription business workflow service.
    
    Handles:
    - Creating new prescriptions  
    - Updating existing prescriptions
    - Managing prescription business rules
    - Coordinating database operations
    
    NOTE: Does NOT handle file I/O - that's the view layer's responsibility
    """
    
    def __init__(self):
        self.pdf_service = PrescriptionPDFService()
        self.logger = logging.getLogger(__name__)
    
    @transaction.atomic
    def create_or_update_prescription(
        self, 
        form_data: dict, 
        user, 
        medico, 
        clinica,
        patient_exists: bool = False,
        process_id: Optional[int] = None
    ) -> Tuple[Optional[HttpResponse], Optional[int]]:
        """
        Create or update a prescription following medical business rules.
        
        Returns:
            Tuple of (pdf_response, process_id) or (None, None) if failed
            View layer is responsible for handling the PDF response (saving to file, etc.)
        """
        # Add comprehensive logging for transaction debugging
        import logging
        db_logger = logging.getLogger('processos.database')
        
        db_logger.info(f"PrescriptionService: Starting transaction for user {user.email}")
        db_logger.info(f"PrescriptionService: Patient exists: {patient_exists}, Process ID: {process_id}")
        
        try:
            # Import services directly to avoid circular imports
            from processos.repositories.medication_repository import MedicationRepository
            from processos.utils.data_utils import link_issuer_data
            from processos.services.registration_service import ProcessRegistrationService
            
            self.logger.info(
                f"PrescriptionService: Processing prescription for "
                f"user: {user.email}, process_id: {process_id}"
            )
            
            # Step 1: Prepare prescription data
            db_logger.info("PrescriptionService: Step 1 - Preparing prescription data")
            med_repo = MedicationRepository()
            medication_ids = med_repo.extract_medication_ids_from_form(form_data)
            form_data, meds_ids = med_repo.format_medication_dosages(form_data, medication_ids)
            final_data = link_issuer_data(user, medico, clinica, form_data)
            db_logger.info(f"PrescriptionService: Data prepared, medications: {len(meds_ids)}")
            
            # Step 2: Validate business rules
            db_logger.info("PrescriptionService: Step 2 - Validating business rules")
            if not self._validate_business_rules(final_data, meds_ids):
                db_logger.error("PrescriptionService: Business rule validation failed")
                return None, None
            
            # Step 3: Get required domain entities
            db_logger.info("PrescriptionService: Step 3 - Getting domain entities")
            cid = form_data.get('cid')
            try:
                doenca = Doenca.objects.get(cid=cid)
                db_logger.info(f"PrescriptionService: Found disease: {doenca.nome}")
            except Doenca.DoesNotExist:
                db_logger.error(f"PrescriptionService: Disease not found for CID: {cid}")
                raise
                
            try:
                emissor = Emissor.objects.get(medico=medico, clinica=clinica)
                db_logger.info(f"PrescriptionService: Found emissor: {emissor.id}")
            except Emissor.DoesNotExist:
                db_logger.error(f"PrescriptionService: Emissor not found for medico/clinica")
                raise
            
            # Step 4: Register prescription in database
            db_logger.info("PrescriptionService: Step 4 - Registering in database")
            # Get actual patient object if exists, not just boolean
            from processos.repositories.patient_repository import PatientRepository
            patient_repo = PatientRepository()
            cpf_paciente = final_data.get('cpf_paciente')
            paciente_obj = patient_repo.check_patient_exists(cpf_paciente) if patient_exists else False
            
            db_logger.info(f"PrescriptionService: CPF: {cpf_paciente}, Patient object: {type(paciente_obj)}")
            
            try:
                registration_service = ProcessRegistrationService()
                processo_id = registration_service.register_process(
                    dados=final_data,
                    meds_ids=meds_ids,
                    doenca=doenca,
                    emissor=emissor,
                    usuario=user,
                    paciente_existe=paciente_obj,
                    cid=cid,
                    processo_id=process_id
                )
                db_logger.info(f"PrescriptionService: Database registration completed with ID: {processo_id}")
            except Exception as db_error:
                db_logger.error(f"PrescriptionService: CRITICAL ERROR in database registration: {db_error}")
                db_logger.error(f"PrescriptionService: Final data keys: {list(final_data.keys())}")
                raise
            
            # Step 5: Generate PDF
            db_logger.info("PrescriptionService: Step 5 - Generating PDF")
            try:
                # Pass user to PDF service for analytics tracking
                pdf_response = self.pdf_service.generate_prescription_pdf(final_data, user=user)
                
                if pdf_response:
                    db_logger.info(
                        f"PrescriptionService: Successfully completed prescription workflow "
                        f"for process ID: {processo_id}"
                    )
                    return pdf_response, processo_id
                else:
                    db_logger.error("PrescriptionService: PDF generation failed")
                    return None, processo_id
            except Exception as pdf_error:
                db_logger.error(f"PrescriptionService: PDF generation error: {pdf_error}")
                # Return the process ID even if PDF fails, so user knows the process was created
                return None, processo_id
                
        except Doenca.DoesNotExist:
            db_logger.error(f"PrescriptionService: Disease not found for CID: {form_data.get('cid')}")
            self.logger.error(f"PrescriptionService: Disease not found for CID: {form_data.get('cid')}")
            raise
        except Emissor.DoesNotExist:
            db_logger.error("PrescriptionService: Emissor not found")
            self.logger.error("PrescriptionService: Emissor not found")
            raise
        except Exception as e:
            db_logger.error(f"PrescriptionService: TRANSACTION FAILED: {e}", exc_info=True)
            self.logger.error(
                f"PrescriptionService: Failed to process prescription: {e}", 
                exc_info=True
            )
            raise
    
    def _validate_business_rules(self, prescription_data: dict, medication_ids: list) -> bool:
        """Validate prescription business rules."""
        # Business rule: Must have at least one medication
        if not medication_ids:
            self.logger.error("PrescriptionService: No medications selected")
            return False
        
        # Business rule: Must have valid prescription dates
        if 'data_1' not in prescription_data:
            self.logger.error("PrescriptionService: Missing prescription start date")
            return False
            
        return True


class RenewalService:
    """
    Prescription renewal business logic service.
    
    Handles renewal workflows with specific medical business rules for renewals.
    """
    
    def __init__(self):
        self.pdf_service = PrescriptionPDFService()
        self.logger = logging.getLogger(__name__)
    
    def process_renewal(
        self, 
        renewal_date: str, 
        process_id: int, 
        user
    ) -> Optional[HttpResponse]:
        """
        Process a prescription renewal following renewal medical business rules.
        
        Renewals have specific rules:
        - No consent forms required
        - No medical reports required
        - No exam requests required
        - Preserves original prescription data with new dates
        """
        try:
            # Use internal method instead of facade import
            
            self.logger.info(
                f"RenewalService: Processing renewal for process {process_id} "
                f"with date {renewal_date} by user {user.email}"
            )
            
            # Validate renewal business rules
            if not self._validate_renewal_eligibility(process_id, user):
                self.logger.error("RenewalService: Process not eligible for renewal")
                return None
            
            # Generate renewal data following renewal rules
            renewal_data = self.generate_renewal_data(renewal_date, process_id, user)
            
            # Generate PDF with user for analytics tracking
            pdf_response = self.pdf_service.generate_prescription_pdf(renewal_data, user=user)
            
            if pdf_response:
                self.logger.info(
                    f"RenewalService: Successfully processed renewal for process {process_id}"
                )
            else:
                self.logger.error("RenewalService: PDF generation failed for renewal")
                
            return pdf_response
            
        except ValueError as e:
            # Handle date validation errors
            self.logger.error(f"RenewalService: Invalid renewal date: {e}")
            raise
        except Processo.DoesNotExist:
            self.logger.error(f"RenewalService: Process {process_id} not found")
            raise
        except Exception as e:
            self.logger.error(
                f"RenewalService: Failed to process renewal: {e}", 
                exc_info=True
            )
            raise
    
    def _validate_renewal_eligibility(self, process_id: int, user) -> bool:
        """Validate if a process is eligible for renewal by the user."""
        try:
            processo = Processo.objects.get(id=process_id)
            
            # Check if user has access to this process
            if processo.usuario != user:
                self.logger.error(
                    f"RenewalService: User {user.email} does not have access to "
                    f"process {process_id}"
                )
                return False
            
            return True
            
        except Processo.DoesNotExist:
            self.logger.error(f"RenewalService: Process {process_id} not found")
            return False
    
    def generate_renewal_data(self, renewal_date: str, process_id: int, user=None) -> dict:
        """
        Generate complete data dictionary for a renewal process.
        
        This method creates a full data dictionary that can be used to create a new process,
        preserving most of the original data but with the updated date and renewal-specific
        modifications.
        
        Args:
            renewal_date: The new start date for the renewal, in DD/MM/YYYY format
            process_id: The ID of the process to be renewed
            user: The user requesting the renewal (for patient versioning)
            
        Returns:
            dict: Complete dictionary of data for the new renewal process
            
        Raises:
            ValueError: If renewal date is invalid or empty
            Processo.DoesNotExist: If process not found
        """
        from datetime import datetime
        from django.forms.models import model_to_dict
        from processos.services.prescription_data_service import PrescriptionDataService
        from processos.repositories.medication_repository import MedicationRepository
        
        self.logger.info(f"RenewalService: Generating renewal data for process {process_id}")
        
        processo = Processo.objects.get(id=process_id)
        dados = {}
        
        # Get versioned patient data if user is provided
        if user:
            paciente_version = processo.paciente.get_version_for_user(user)
            if paciente_version:
                paciente_data = model_to_dict(paciente_version)
                # Keep master record fields that aren't versioned
                paciente_data['id'] = processo.paciente.id
                paciente_data['cpf_paciente'] = processo.paciente.cpf_paciente
                paciente_data['usuarios'] = processo.paciente.usuarios.all()
            else:
                paciente_data = model_to_dict(processo.paciente)
        else:
            # Fallback to master record if no user provided
            paciente_data = model_to_dict(processo.paciente)
        
        # Collect all related data
        data_sources = [
            model_to_dict(processo),
            paciente_data,
            model_to_dict(processo.medico),
            model_to_dict(processo.clinica),
        ]
        
        for data_source in data_sources:
            dados.update(data_source)
        
        # pdftk requires string inputs, not object references
        dados["medicos"] = ""
        dados["usuarios"] = ""
        dados["medicamentos"] = ""
        
        # Build clinic address
        end_clinica = dados["logradouro"] + ", " + dados["logradouro_num"]
        dados["end_clinica"] = end_clinica
        
        # Validate and parse renewal date
        if not renewal_date or renewal_date.strip() == "":
            raise ValueError("Data de renovação não pode estar vazia")
        
        try:
            dados["data_1"] = datetime.strptime(renewal_date, "%d/%m/%Y")
        except ValueError as e:
            raise ValueError(f"Formato de data inválido: {renewal_date}. Use DD/MM/AAAA")
        
        # Set disease information
        dados["cid"] = processo.doenca.cid
        dados["diagnostico"] = processo.doenca.nome
        
        # CRITICAL: Setting conditional PDF flags for renovation
        dados["consentimento"] = False  # No consent for renewals
        dados["relatorio"] = False      # No report for renewals 
        dados["exames"] = False         # No exams for renewals
        
        # Handle chronic pain special logic
        try:
            protocolo = processo.doenca.protocolo
            
            if protocolo.nome == "dor_crônica":
                # For chronic pain, include the LANNS/EVA assessment form
                dados["include_lanns_eva"] = True
                
                # Preserve any conditional data from original process
                if processo.dados_condicionais:
                    for key, value in processo.dados_condicionais.items():
                        dados[key] = value
        except Exception:
            # Silently handle any protocol-related errors
            pass
        
        # Retrieve prescription data from original process
        prescription_service = PrescriptionDataService()
        dados = prescription_service.retrieve_prescription_data(dados, processo)
        
        # Generate medication information
        med_repo = MedicationRepository()
        meds_ids = med_repo.extract_medication_ids_from_form(dados)
        dados, _ = med_repo.format_medication_dosages(dados, meds_ids)
        
        self.logger.info(f"RenewalService: Generated renewal data with {len(meds_ids)} medications")
        return dados
    
    def create_renewal_dictionary(self, processo: Processo, user=None) -> dict:
        """
        Create a dictionary with data for a renewal process.
        
        This method extracts necessary data from a Processo model instance to create
        a new renewal process, handling patient versioning appropriately.
        
        Args:
            processo: The Django model instance to get the data from
            user: The user to get versioned patient data for (required for patient data)
            
        Returns:
            dict: Dictionary containing the data for the renewal process
            
        Raises:
            ValueError: If user is not provided or has no access to patient
        """
        from django.forms.models import model_to_dict
        
        if not user:
            raise ValueError("User parameter is required for accessing patient data")
        
        # Get versioned patient data - no fallback to prevent data breach
        paciente_version = processo.paciente.get_version_for_user(user)
        if not paciente_version:
            raise ValueError(f"User {user.email} has no access to patient {processo.paciente.cpf_paciente}")
        
        # Use Django's model_to_dict with field filtering for maintainability
        needed_fields = [
            'nome_paciente', 'peso', 'altura', 'nome_mae', 'incapaz', 
            'nome_responsavel', 'etnia', 'telefone1_paciente', 
            'telefone2_paciente', 'email_paciente', 'end_paciente'
        ]
        patient_data = model_to_dict(paciente_version, fields=needed_fields)
        # Override with master CPF (security requirement)
        patient_data['cpf_paciente'] = processo.paciente.cpf_paciente
        
        # Use model_to_dict for process data as well
        process_fields = [
            'prescricao', 'anamnese', 'tratou', 'tratamentos_previos', 'preenchido_por'
        ]
        process_data = model_to_dict(processo, fields=process_fields)
        
        # Add related field data manually (foreign keys need special handling)
        process_data.update({
            "cid": processo.doenca.cid,
            "diagnostico": processo.doenca.nome,
            "clinica": processo.clinica,
        })
        
        # Combine patient and process data
        dicionario = {
            **patient_data,  # Unpack patient data
            **process_data,  # Unpack process data
        }
        
        # Add conditional data from the process
        if processo.dados_condicionais:
            dicionario.update(processo.dados_condicionais)
            
        return dicionario