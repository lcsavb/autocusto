"""
Patient Repository - Patient Data Access Layer

This repository handles patient data access patterns, queries, and validation.
It provides a clean interface for patient-related database operations.

Extracted from helpers.py to follow repository pattern principles.
"""

import logging
from typing import Dict, Any, Optional, Union
from django.db.models import QuerySet

from pacientes.models import Paciente


class PatientRepository:
    """
    Repository for patient data access and validation operations.
    
    This repository encapsulates all patient-related database operations including:
    - Patient existence checks
    - Patient data extraction and formatting
    - Patient query operations
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def check_patient_exists(self, cpf_paciente: str) -> Union[Paciente, bool]:
        """
        Check if a patient with the given CPF exists in the database.
        
        This method performs a database lookup to determine if a patient record
        exists for the provided CPF. It's commonly used in form validation
        and process creation workflows.
        
        Args:
            cpf_paciente: The patient's CPF (Brazilian tax ID)
            
        Returns:
            Paciente: The patient instance if found
            bool: False if patient does not exist
        """
        self.logger.debug(f"PatientRepository: Checking existence for CPF {cpf_paciente}")
        
        try:
            patient = Paciente.objects.get(cpf_paciente=cpf_paciente)
            self.logger.debug(f"PatientRepository: Patient found with ID {patient.id}")
            return patient
        except Paciente.DoesNotExist:
            self.logger.debug(f"PatientRepository: No patient found for CPF {cpf_paciente}")
            return False
    
    def extract_patient_data(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract patient-specific data from a larger form data dictionary.
        
        This method separates patient data from other form data, creating a clean
        dictionary that contains only patient-related fields. This is useful for
        patient creation and update operations.
        
        Args:
            form_data: The complete form data dictionary
            
        Returns:
            dict: Dictionary containing only patient data fields
        """
        self.logger.debug("PatientRepository: Extracting patient data from form")
        
        # Define patient-specific fields
        patient_fields = [
            'nome_paciente', 'cpf_paciente', 'peso', 'altura', 'nome_mae',
            'incapaz', 'nome_responsavel', 'etnia', 'telefone1_paciente',
            'telefone2_paciente', 'email_paciente', 'end_paciente'
        ]
        
        # Extract only patient fields from form data
        patient_data = {}
        extracted_count = 0
        
        for field in patient_fields:
            if field in form_data:
                patient_data[field] = form_data[field]
                extracted_count += 1
        
        self.logger.debug(f"PatientRepository: Extracted {extracted_count} patient fields")
        return patient_data
    
    def get_patients_by_user(self, user) -> QuerySet:
        """
        Get all patients accessible by a specific user.
        
        This method returns patients that the user has access to through
        the versioning system, respecting data access permissions.
        
        Args:
            user: The user to get patients for
            
        Returns:
            QuerySet: QuerySet of accessible patient records
        """
        self.logger.debug(f"PatientRepository: Getting patients for user {user.email}")
        
        # This would depend on the specific patient versioning implementation
        # For now, return patients where user has versions
        accessible_patients = Paciente.objects.filter(
            versions__usuario=user
        ).distinct()
        
        count = accessible_patients.count()
        self.logger.debug(f"PatientRepository: Found {count} accessible patients")
        
        return accessible_patients
    
    def get_patient_version_for_user(self, patient: Paciente, user) -> Optional[Any]:
        """
        Get the patient data version for a specific user.
        
        This method retrieves the patient data version that the user has access to,
        implementing the patient versioning security model.
        
        Args:
            patient: The patient instance
            user: The user requesting access
            
        Returns:
            Patient version instance if found, None otherwise
        """
        self.logger.debug(f"PatientRepository: Getting version for patient {patient.id}, user {user.email}")
        
        try:
            patient_version = patient.get_version_for_user(user)
            if patient_version:
                self.logger.debug(f"PatientRepository: Found version {patient_version.id}")
            else:
                self.logger.debug("PatientRepository: No version found for user")
            return patient_version
        except Exception as e:
            self.logger.error(f"PatientRepository: Error getting patient version: {e}")
            return None
    
    def validate_patient_data(self, patient_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate patient data and return validation errors.
        
        This method performs business rule validation on patient data,
        checking for required fields and data format compliance.
        
        Args:
            patient_data: Dictionary containing patient data to validate
            
        Returns:
            dict: Dictionary of validation errors (empty if valid)
        """
        self.logger.debug("PatientRepository: Validating patient data")
        
        errors = {}
        
        # Required fields validation
        required_fields = ['nome_paciente', 'cpf_paciente']
        for field in required_fields:
            if not patient_data.get(field):
                errors[field] = f"{field} é obrigatório"
        
        # CPF format validation (basic check)
        cpf = patient_data.get('cpf_paciente', '')
        if cpf and len(cpf.replace('.', '').replace('-', '')) != 11:
            errors['cpf_paciente'] = "CPF deve ter 11 dígitos"
        
        # Email validation (if provided)
        email = patient_data.get('email_paciente', '')
        if email and '@' not in email:
            errors['email_paciente'] = "Email inválido"
        
        error_count = len(errors)
        self.logger.debug(f"PatientRepository: Validation completed with {error_count} errors")
        
        return errors