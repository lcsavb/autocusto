"""
Prescription Renewal Service

Prescription renewal business logic service.
Handles renewal workflows with specific medical business rules for renewals.

Extracted from prescription_services.py to follow single responsibility principle.
"""

import logging
from typing import Optional
from datetime import datetime
from django.http import HttpResponse
from django.forms.models import model_to_dict

from processos.models import Processo
from .pdf_generation import PrescriptionPDFService


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
            from ...repositories.process_repository import ProcessRepository
            process_repo = ProcessRepository()
            processo = process_repo.get_process_for_user(process_id, user)
            return processo is not None
            
        except Exception as e:
            self.logger.error(f"RenewalService: Error validating process {process_id}: {e}")
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
        from processos.repositories.medication_repository import MedicationRepository
        
        self.logger.info(f"RenewalService: Generating renewal data for process {process_id}")
        
        # Verify user owns this process before accessing data
        from ...repositories.process_repository import ProcessRepository
        process_repo = ProcessRepository()
        
        if user:
            processo = process_repo.get_process_for_user(process_id, user)
            if not processo:
                raise Processo.DoesNotExist(f"Process {process_id} not found for user")
        else:
            # Fallback for cases where user is not provided (should be rare)
            processo = process_repo.get_process_by_id(process_id)
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
        
        # Validate renewal date - expects a date object
        if not renewal_date:
            raise ValueError("Data de renovação não pode estar vazia")
        
        # Use the date object directly
        dados["data_1"] = renewal_date
        
        # Set disease information
        dados["cid"] = processo.doenca.cid
        dados["diagnostico"] = processo.doenca.nome
        
        # CRITICAL: Setting conditional PDF flags for renovation
        dados["consentimento"] = False  # No consent for renewals
        dados["relatorio"] = False      # No report for renewals 
        dados["exames"] = False         # No exams for renewals
        
        # Preserve conditional data from original process for ALL protocols
        if processo.dados_condicionais:
            for key, value in processo.dados_condicionais.items():
                dados[key] = value
        
       
        # Retrieve prescription data from original process
        dados = self._retrieve_prescription_data(dados, processo)
        
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
    
    def _retrieve_prescription_data(self, dados: dict, processo: Processo) -> dict:
        """
        Populate a data dictionary with prescription details from a Processo object.
        
        This method transfers prescription information from the structured
        `processo.prescricao` field into a flat `dados` dictionary. This flattening
        is necessary to populate form fields for display or editing.
        
        Args:
            dados: The dictionary to populate with prescription data (modified in-place)
            processo: The Django model instance containing the prescription to retrieve
            
        Returns:
            dict: The updated `dados` dictionary with flattened prescription information
        """
        self.logger.debug(f"RenewalService: Retrieving prescription for process {processo.id}")
        
        medication_counter = 1
        prescricao = processo.prescricao
        
        # The `prescricao` field stores medication data in nested structure:
        # {
        #   '1': {'id_med1': 123, 'med1_posologia_mes1': '...'},
        #   '2': {'id_med2': 456, 'med2_posologia_mes1': '...'}
        # }
        for med_number, med_data in prescricao.items():
            if med_number != "":
                # Set medication ID
                dados[f"id_med{medication_counter}"] = med_data[f"id_med{medication_counter}"]
                
                # Unpack all medication details into main data dictionary
                for field_name, field_value in med_data.items():
                    dados[field_name] = field_value
                    
                medication_counter += 1
        
        self.logger.debug(f"RenewalService: Retrieved {medication_counter-1} medications")
        return dados