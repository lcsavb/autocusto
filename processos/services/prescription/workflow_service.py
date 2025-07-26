"""
Prescription Workflow Service

Complete prescription business workflow service.
Handles creating new prescriptions, updating existing prescriptions, and managing prescription business rules.

Extracted from prescription_services.py to follow single responsibility principle.
"""

import logging
from typing import Tuple, Optional
from django.http import HttpResponse
from django.db import transaction

from processos.models import Doenca
from clinicas.models import Emissor
from .pdf_generation import PrescriptionPDFService
from .data_builder import PrescriptionDataBuilder
from .process_repository import ProcessRepository
from ...repositories.domain_repository import DomainRepository


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
        self.data_builder = PrescriptionDataBuilder()
        self.process_repository = ProcessRepository()
        self.domain_repository = DomainRepository()
    
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
            
            # Step 3: Get required domain entities using DomainRepository
            db_logger.info("PrescriptionService: Step 3 - Getting domain entities")
            cid = form_data.get('cid')
            doenca = self.domain_repository.get_disease_by_cid(cid)
            emissor = self.domain_repository.get_emissor_by_medico_clinica(medico, clinica)
            
            # Step 4: Process prescription using service layer (clean architecture)
            db_logger.info("PrescriptionService: Step 4 - Processing via service layer")
            
            try:
                # Use our clean service architecture instead of forms
                from processos.repositories.patient_repository import PatientRepository
                patient_repo = PatientRepository()
                cpf_paciente = final_data["cpf_paciente"]
                paciente_existe = patient_repo.check_patient_exists(cpf_paciente)
                
                # Build structured data using DataBuilder
                structured_data = self.data_builder.build_prescription_data(
                    final_data, meds_ids, doenca, emissor, user,
                    paciente_existe=paciente_existe, 
                    cid=cid, 
                    processo_id=process_id
                )
                
                # Save using ProcessRepository
                if process_id:
                    # Update existing prescription
                    db_logger.info(f"PrescriptionService: Updating process {process_id} via service layer")
                    processo_id = self.process_repository.update_process_from_structured_data(
                        process_id, structured_data
                    )
                else:
                    # Create new prescription  
                    db_logger.info("PrescriptionService: Creating new process via service layer")
                    processo_id = self.process_repository.create_process_from_structured_data(
                        structured_data
                    )
                
                db_logger.info(f"PrescriptionService: Process saved with ID: {processo_id}")
                    
            except Exception as db_error:
                db_logger.error(f"PrescriptionService: CRITICAL ERROR in service layer: {db_error}")
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