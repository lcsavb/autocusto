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
from ..services.prescription.patient_versioning_service import PatientVersioningService


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
        self.patient_versioning = PatientVersioningService()
    
    def check_patient_exists(self, cpf_paciente: str) -> Union[Paciente, bool]:
        """
        Check if patient exists - crucial for prescription workflow routing.
        
        Return type determines workflow: Paciente object for updates, False for new patient creation.
        CPF (Cadastro de Pessoas Físicas) is Brazilian national ID - unique patient identifier.
        
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
        
        # Brazilian medical form fields - matches ANVISA prescription requirements
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
        Get user's accessible patients - enforces versioning security boundaries.
        
        LGPD compliance: Users only see patients they've personally entered data for,
        preventing unauthorized access to other medical professionals' patient records.
        
        Args:
            user: The user to get patients for
            
        Returns:
            QuerySet: QuerySet of accessible patient records
        """
        self.logger.debug(f"PatientRepository: Getting patients for user {user.email}")
        
        # Privacy enforcement: Only return patients where user has created versions
        # This prevents cross-contamination of patient data between medical professionals
        accessible_patients = Paciente.objects.filter(
            versions__usuario=user
        ).distinct()
        
        count = accessible_patients.count()
        self.logger.debug(f"PatientRepository: Found {count} accessible patients")
        
        return accessible_patients
    
    def get_patient_version_for_user(self, patient: Paciente, user):
        """
        Get the patient data version for a specific user.
        
        This method retrieves the patient data version that the user has access to,
        implementing the patient versioning security model.
        
        Args:
            patient: The patient instance
            user: The user requesting access
            
        Returns:
            Patient version instance if found
            
        Raises:
            ValueError: If no patient version exists for this user
        """
        self.logger.debug(f"PatientRepository: Getting version for patient {patient.id}, user {user.email}")
        
        version = self.patient_versioning.get_patient_version_for_user(patient.cpf_paciente, user)
        
        if version is None:
            self.logger.warning(f"PatientRepository: No version found for patient {patient.id}, user {user.email}")
            raise ValueError(f"No patient data version exists for user {user.email}. Patient data must be entered through proper workflow.")
        
        return version
    
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
        
        # Brazilian medical compliance: Name and CPF mandatory for prescription validity
        required_fields = ['nome_paciente', 'cpf_paciente']
        for field in required_fields:
            if not patient_data.get(field):
                errors[field] = f"{field} é obrigatório"
        
        # CPF validation: Must be exactly 11 digits (Brazilian tax ID format)
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
    
    def get_patient_by_id(self, patient_id: int) -> Optional[Paciente]:
        """
        Get patient by ID.
        
        Args:
            patient_id: The patient's ID
            
        Returns:
            Paciente: The patient instance if found
            
        Raises:
            Paciente.DoesNotExist: If patient not found
        """
        self.logger.debug(f"PatientRepository: Getting patient by ID {patient_id}")
        
        try:
            patient = Paciente.objects.get(id=patient_id)
            self.logger.debug(f"PatientRepository: Patient found with CPF {patient.cpf_paciente}")
            return patient
        except Paciente.DoesNotExist:
            self.logger.error(f"PatientRepository: Patient not found for ID: {patient_id}")
            raise