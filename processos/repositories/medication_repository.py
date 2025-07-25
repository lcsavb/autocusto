"""
Medication Repository - Medication Data Access Layer

This repository handles medication data access patterns, queries, and associations.
It provides a clean interface for medication-related database operations.

Extracted from helpers.py to follow repository pattern principles.
"""

import logging
from typing import List, Tuple, Dict, Any
from django.db.models import QuerySet

from processos.models import Medicamento, Protocolo, Processo


class MedicationRepository:
    """
    Repository for medication data access and association operations.
    
    This repository encapsulates all medication-related database operations including:
    - Medication queries by protocol/CID
    - Medication association with processes
    - Medication data formatting and presentation
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def list_medications_by_cid(self, cid: str) -> Tuple[Tuple[str, str], ...]:
        """
        Retrieve medications associated with a protocol and return formatted list.
        
        This method fetches medications appropriate for a given CID (International
        Classification of Diseases) code and formats them for use in form dropdowns.
        
        Args:
            cid: The CID code for the disease
            
        Returns:
            tuple: Tuple of tuples, each containing (medication_id, display_string)
        """
        self.logger.debug(f"MedicationRepository: Listing medications for CID {cid}")
        
        try:
            # Get protocol associated with the CID
            protocol = Protocolo.objects.get(doenca__cid=cid)
            medications = protocol.medicamentos.all()
            
            # Build medication list with default option
            medication_list = [("nenhum", "Escolha o medicamento...")]
            
            for medication in medications:
                display_name = f"{medication.nome} {medication.dosagem} - {medication.apres}"
                medication_tuple = (medication.id, display_name)
                medication_list.append(medication_tuple)
            
            self.logger.debug(f"MedicationRepository: Found {len(medication_list)-1} medications for CID {cid}")
            return tuple(medication_list)
            
        except Protocolo.DoesNotExist:
            self.logger.error(f"MedicationRepository: No protocol found for CID {cid}")
            return (("nenhum", "Nenhum medicamento disponível"),)
    
    def get_medication_details(self, medication_id: int) -> Dict[str, str]:
        """
        Get detailed information about a specific medication.
        
        Args:
            medication_id: The ID of the medication
            
        Returns:
            dict: Medication details including nome, dosagem, apres
        """
        self.logger.debug(f"MedicationRepository: Getting details for medication {medication_id}")
        
        try:
            medication = Medicamento.objects.get(id=medication_id)
            details = {
                'nome': medication.nome,
                'dosagem': medication.dosagem,
                'apres': medication.apres,
                'formatted': f"{medication.nome} {medication.dosagem} ({medication.apres})"
            }
            self.logger.debug(f"MedicationRepository: Retrieved details for {medication.nome}")
            return details
        except Medicamento.DoesNotExist:
            self.logger.error(f"MedicationRepository: Medication {medication_id} not found")
            return {}
    
    def format_medication_dosages(
        self, 
        form_data: Dict[str, Any], 
        medication_ids: List[str]
    ) -> Tuple[Dict[str, Any], List[str]]:
        """
        Retrieve medication details and format them for PDF generation.
        
        This method fetches full medication details from the database and formats
        them into strings suitable for PDF form filling with pdftk.
        
        Args:
            form_data: The main dictionary of form data (modified in-place)
            medication_ids: List of medication IDs selected in the form
            
        Returns:
            tuple: (updated_form_data, cleaned_medication_ids)
        """
        self.logger.debug(f"MedicationRepository: Formatting dosages for {len(medication_ids)} medications")
        
        cleaned_ids = []
        
        for index, med_id in enumerate(medication_ids, 1):
            if med_id != "nenhum":
                cleaned_ids.append(med_id)
                
                try:
                    medication = Medicamento.objects.get(id=med_id)
                    formatted_med = f"{medication.nome} {medication.dosagem} ({medication.apres})"
                    form_data[f"med{index}"] = formatted_med
                    
                    self.logger.debug(f"MedicationRepository: Formatted med{index}: {medication.nome}")
                except Medicamento.DoesNotExist:
                    self.logger.error(f"MedicationRepository: Medication {med_id} not found")
                    form_data[f"med{index}"] = "Medicamento não encontrado"
        
        self.logger.debug(f"MedicationRepository: Formatted {len(cleaned_ids)} valid medications")
        return form_data, cleaned_ids
    
    def associate_medications_with_process(self, processo: Processo, medication_ids: List[str]) -> None:
        """
        Synchronize medications associated with a process.
        
        This method ensures that the medications linked to a process match the
        provided list of medication IDs, adding new ones and removing outdated ones.
        
        Args:
            processo: The process instance to update
            medication_ids: List of medication IDs that should be associated
        """
        self.logger.debug(f"MedicationRepository: Associating {len(medication_ids)} medications with process {processo.id}")
        
        # Add new medications
        for med_id in medication_ids:
            try:
                processo.medicamentos.add(med_id)
            except Exception as e:
                self.logger.error(f"MedicationRepository: Error adding medication {med_id}: {e}")
        
        # Remove medications not in the new list
        current_medications = processo.medicamentos.all()
        removed_count = 0
        
        for current_med in current_medications:
            if str(current_med.id) not in medication_ids:
                processo.medicamentos.remove(current_med)
                removed_count += 1
        
        self.logger.debug(f"MedicationRepository: Association complete, removed {removed_count} outdated medications")
    
    def extract_medication_ids_from_form(self, form_data: Dict[str, Any]) -> List[str]:
        """
        Extract medication IDs from form data.
        
        This method iterates through form data and extracts medication IDs
        from fields like `id_med1`, `id_med2`, etc.
        
        Args:
            form_data: The form data dictionary
            
        Returns:
            list: List of valid medication IDs
        """
        self.logger.debug("MedicationRepository: Extracting medication IDs from form data")
        
        medication_ids = []
        med_counter = 1
        
        while med_counter <= 4:  # Support up to 4 medications
            try:
                med_id_key = f"id_med{med_counter}"
                if med_id_key in form_data and form_data[med_id_key] != "nenhum":
                    medication_ids.append(form_data[med_id_key])
            except KeyError:
                # Continue if key is missing (no more medications)
                pass
            med_counter += 1
        
        self.logger.debug(f"MedicationRepository: Extracted {len(medication_ids)} medication IDs")
        return medication_ids
    
    def get_medications_by_protocol(self, protocol_name: str) -> QuerySet:
        """
        Get all medications associated with a specific protocol.
        
        Args:
            protocol_name: Name of the medical protocol
            
        Returns:
            QuerySet: QuerySet of medications for the protocol
        """
        self.logger.debug(f"MedicationRepository: Getting medications for protocol {protocol_name}")
        
        try:
            protocol = Protocolo.objects.get(nome=protocol_name)
            medications = protocol.medicamentos.all()
            
            count = medications.count()
            self.logger.debug(f"MedicationRepository: Found {count} medications for protocol {protocol_name}")
            
            return medications
        except Protocolo.DoesNotExist:
            self.logger.error(f"MedicationRepository: Protocol {protocol_name} not found")
            return Medicamento.objects.none()
    
    def validate_medication_selection(self, medication_ids: List[str]) -> Dict[str, str]:
        """
        Validate medication selection and return validation errors.
        
        Args:
            medication_ids: List of medication IDs to validate
            
        Returns:
            dict: Dictionary of validation errors (empty if valid)
        """
        self.logger.debug(f"MedicationRepository: Validating {len(medication_ids)} medication selections")
        
        errors = {}
        
        # Check if at least one medication is selected
        if not medication_ids:
            errors['medications'] = "Pelo menos um medicamento deve ser selecionado"
        
        # Validate each medication exists
        for index, med_id in enumerate(medication_ids, 1):
            try:
                Medicamento.objects.get(id=med_id)
            except Medicamento.DoesNotExist:
                errors[f'id_med{index}'] = f"Medicamento {med_id} não encontrado"
        
        error_count = len(errors)
        self.logger.debug(f"MedicationRepository: Validation completed with {error_count} errors")
        
        return errors