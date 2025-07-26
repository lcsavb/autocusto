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