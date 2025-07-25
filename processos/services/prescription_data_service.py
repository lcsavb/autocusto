"""
Prescription Data Service - Prescription Data Manipulation Business Logic

This service handles prescription-specific data operations including prescription
creation, retrieval, and data manipulation. It contains domain knowledge about
prescription structure and validation rules.

Extracted from helpers.py to follow service-oriented architecture principles.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from processos.models import Processo


class PrescriptionDataService:
    """
    Service for handling prescription data manipulation and validation.
    
    This service encapsulates prescription-specific business logic including:
    - Prescription data structure creation and retrieval
    - Prescription validation and formatting
    - Process data generation with prescription context
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def retrieve_prescription_data(self, dados: Dict[str, Any], processo: Processo) -> Dict[str, Any]:
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
        self.logger.debug(f"PrescriptionDataService: Retrieving prescription for process {processo.id}")
        
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
        
        self.logger.debug(f"PrescriptionDataService: Retrieved {medication_counter-1} medications")
        return dados
    
    def generate_prescription_structure(self, meds_ids: List[str], form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Construct a structured prescription dictionary from form data.
        
        This method builds the nested dictionary structure that represents the prescription
        as stored in the Processo model. It organizes dosage and quantity for each
        medication over a six-month period.
        
        Args:
            meds_ids: List of medication IDs to include in the prescription
            form_data: Flat dictionary containing form data with medication details
            
        Returns:
            dict: Nested prescription structure ready for Processo.prescricao field
        """
        self.logger.debug(f"PrescriptionDataService: Generating prescription for {len(meds_ids)} medications")
        
        prescricao = {}
        
        for med_index, med_id in enumerate(meds_ids, 1):
            med_prescricao = {'id_med{}'.format(med_index): med_id}
            
            # Generate prescription data for 6-month period
            for month in range(1, 7):
                posologia_key = f"med{med_index}_posologia_mes{month}"
                quantity_key = f"qtd_med{med_index}_mes{month}"
                
                med_prescricao[posologia_key] = form_data[posologia_key]
                med_prescricao[quantity_key] = form_data[quantity_key]
            
            # Add administration route for first medication
            if med_index == 1:
                med_prescricao["med1_via"] = form_data["med1_via"]
            
            prescricao[med_index] = med_prescricao
        
        self.logger.debug(f"PrescriptionDataService: Generated prescription structure with {len(prescricao)} medications")
        return prescricao
    
    def generate_process_data(
        self,
        form_data: Dict[str, Any],
        meds_ids: List[str],
        doenca,
        emissor,
        paciente,
        usuario
    ) -> Dict[str, Any]:
        """
        Create a complete process data dictionary from form inputs.
        
        This method generates the structured data dictionary used to create
        a new Processo object, including prescription structure and conditional data.
        
        Args:
            form_data: Complete form data dictionary
            meds_ids: List of medication IDs
            doenca: Disease instance
            emissor: Issuer (doctor-clinic combination)
            paciente: Patient instance
            usuario: User instance
            
        Returns:
            dict: Complete process data dictionary ready for Processo creation
        """
        self.logger.debug(f"PrescriptionDataService: Generating process data for {len(meds_ids)} medications")
        
        # Generate prescription structure
        prescricao = self.generate_prescription_structure(meds_ids, form_data)
        
        # Build process data dictionary
        process_data = {
            'prescricao': prescricao,
            'anamnese': form_data["anamnese"],
            'tratou': form_data["tratou"],
            'tratamentos_previos': form_data["tratamentos_previos"],
            'doenca': doenca,
            'preenchido_por': form_data["preenchido_por"],
            'medico': emissor.medico,
            'paciente': paciente,
            'clinica': emissor.clinica,
            'emissor': emissor,
            'usuario': usuario,
            'dados_condicionais': {},
        }
        
        # Extract conditional data (protocol-specific fields starting with 'opt_')
        conditional_data_count = 0
        for field_name, field_value in form_data.items():
            if field_name.startswith("opt_"):
                process_data["dados_condicionais"][field_name] = field_value
                conditional_data_count += 1
        
        self.logger.debug(
            f"PrescriptionDataService: Generated process data with {conditional_data_count} conditional fields"
        )
        return process_data
    
    def extract_partial_edit_data(self, form_data: Dict[str, Any], process_id: int) -> tuple:
        """
        Generate data dictionary for partial process updates.
        
        This method creates a dictionary with the specific data that should be updated
        during a partial renewal, along with the list of fields to update.
        
        Args:
            form_data: The form data dictionary
            process_id: The ID of the process to be updated
            
        Returns:
            tuple: (update_data_dict, fields_to_update_list)
        """
        self.logger.debug(f"PrescriptionDataService: Generating partial edit data for process {process_id}")
        
        # Extract medication IDs from form data
        medication_ids = self._extract_medication_ids(form_data)
        
        # Generate prescription structure
        prescricao = self.generate_prescription_structure(medication_ids, form_data)
        
        # Create update data dictionary
        update_data = {
            'id': process_id,
            'data1': form_data["data_1"],
            'prescricao': prescricao
        }
        
        # Generate list of fields to update (excluding ID)
        fields_to_update = [key for key in update_data.keys() if key != 'id']
        
        self.logger.debug(
            f"PrescriptionDataService: Generated partial edit data with {len(fields_to_update)} fields to update"
        )
        return update_data, fields_to_update
    
    def _extract_medication_ids(self, form_data: Dict[str, Any]) -> List[str]:
        """
        Extract medication IDs from form data.
        
        This helper method iterates through form data and extracts medication IDs
        from fields like `id_med1`, `id_med2`, etc.
        
        Args:
            form_data: The form data dictionary
            
        Returns:
            list: List of medication IDs
        """
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
        
        return medication_ids