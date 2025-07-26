"""
Doctor Profile Service - Doctor Profile Management Business Logic

This service handles the complex business logic for managing doctor profiles,
including profile completion, updates, and validation of medical credentials.
"""

import logging
from typing import Dict, Any, Optional, List
from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from medicos.repositories.doctor_repository import DoctorRepository

User = get_user_model()
logger = logging.getLogger('medicos.services')


class DoctorProfileService:
    """
    Service for handling doctor profile management business logic.
    
    This service encapsulates the workflow of:
    - Doctor profile completion (CRM, CNS, specialty)
    - Profile updates and modifications
    - Medical credential validation
    - Profile status management
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.doctor_repository = DoctorRepository()
    
    @transaction.atomic
    def complete_doctor_profile(self, user: User, profile_data: Dict[str, Any]) -> Any:
        """
        Complete a doctor's profile with professional information.
        
        This handles the profile completion workflow after initial registration:
        1. Validate professional credentials
        2. Update doctor profile with CRM, CNS, specialty
        3. Mark profile as complete
        4. Set up professional settings
        
        Args:
            user: The user whose profile to complete
            profile_data: Profile completion form data
            
        Returns:
            Medico: Updated doctor instance
            
        Raises:
            ValidationError: If profile data is invalid
            ValueError: If user has no doctor profile
        """
        self.logger.info(f"DoctorProfileService: Completing profile for user {user.email}")
        
        try:
            # Get existing doctor profile
            doctor = self.doctor_repository.get_doctor_by_user(user)
            if not doctor:
                raise ValueError("User has no associated doctor profile")
            
            # Extract and normalize doctor data
            doctor_data = self.doctor_repository.extract_doctor_data(profile_data)
            
            # Update doctor profile
            updated_doctor = self.doctor_repository.update_doctor(doctor, doctor_data)
            
            # Set up professional settings if this is the first completion
            if self._is_first_completion(doctor, doctor_data):
                self._setup_professional_settings(user, updated_doctor)
            
            self.logger.info(f"DoctorProfileService: Profile completed for doctor {updated_doctor.id}")
            return updated_doctor
            
        except Exception as e:
            self.logger.error(f"DoctorProfileService: Profile completion failed: {e}")
            raise
    
    @transaction.atomic
    def update_doctor_profile(self, user: User, update_data: Dict[str, Any]) -> Any:
        """
        Update an existing doctor profile with new information.
        
        Args:
            user: The user whose profile to update
            update_data: Updated profile data
            
        Returns:
            Medico: Updated doctor instance
            
        Raises:
            ValidationError: If update data is invalid
            ValueError: If user has no doctor profile
        """
        self.logger.info(f"DoctorProfileService: Updating profile for user {user.email}")
        
        try:
            # Get existing doctor profile
            doctor = self.doctor_repository.get_doctor_by_user(user)
            if not doctor:
                raise ValueError("User has no associated doctor profile")
            
            # Extract and normalize doctor data
            doctor_data = self.doctor_repository.extract_doctor_data(update_data)
            
            # Update doctor profile
            updated_doctor = self.doctor_repository.update_doctor(doctor, doctor_data)
            
            self.logger.info(f"DoctorProfileService: Profile updated for doctor {updated_doctor.id}")
            return updated_doctor
            
        except Exception as e:
            self.logger.error(f"DoctorProfileService: Profile update failed: {e}")
            raise
    
    def get_profile_completion_status(self, user: User) -> Dict[str, Any]:
        """
        Get the completion status of a doctor's profile.
        
        Args:
            user: The user to check
            
        Returns:
            dict: Profile completion status information
        """
        self.logger.debug(f"DoctorProfileService: Checking profile status for user {user.email}")
        
        doctor = self.doctor_repository.get_doctor_by_user(user)
        if not doctor:
            return {
                'has_profile': False,
                'is_complete': False,
                'missing_fields': ['doctor_profile'],
                'completion_percentage': 0
            }
        
        # Check required fields for completion
        required_fields = {
            'nome_medico': doctor.nome_medico,
            'crm_medico': doctor.crm_medico,
            'cns_medico': doctor.cns_medico,
            'estado': doctor.estado,
            'especialidade': doctor.especialidade
        }
        
        completed_fields = {k: v for k, v in required_fields.items() if v}
        missing_fields = [k for k, v in required_fields.items() if not v]
        
        completion_percentage = int((len(completed_fields) / len(required_fields)) * 100)
        is_complete = len(missing_fields) == 0
        
        status = {
            'has_profile': True,
            'is_complete': is_complete,
            'completed_fields': list(completed_fields.keys()),
            'missing_fields': missing_fields,
            'completion_percentage': completion_percentage
        }
        
        self.logger.debug(f"DoctorProfileService: Profile completion: {completion_percentage}%")
        return status
    
    def _is_first_completion(self, doctor, doctor_data: Dict[str, Any]) -> bool:
        """
        Check if this is the first time the profile is being completed.
        
        Args:
            doctor: Doctor instance
            doctor_data: New doctor data
            
        Returns:
            bool: True if this is first completion
        """
        return not doctor.crm_medico and doctor_data.get('crm_medico')
    
    def _setup_professional_settings(self, user: User, doctor) -> None:
        """
        Set up professional settings for newly completed profiles.
        
        Args:
            user: User instance
            doctor: Doctor instance
        """
        self.logger.debug(f"DoctorProfileService: Setting up professional settings for doctor {doctor.id}")
        
        # Mark user as having completed profile
        # This could be extended with professional-specific settings
        
        self.logger.debug(f"DoctorProfileService: Professional settings complete for doctor {doctor.id}")
    
    def get_doctor_professional_info(self, user: User) -> Optional[Dict[str, Any]]:
        """
        Get professional information for a doctor.
        
        Args:
            user: User to get info for
            
        Returns:
            dict: Professional information or None if no doctor profile
        """
        doctor = self.doctor_repository.get_doctor_by_user(user)
        if not doctor:
            return None
        
        return {
            'nome': doctor.nome_medico,
            'crm': doctor.crm_medico,
            'cns': doctor.cns_medico,
            'estado': doctor.estado,
            'especialidade': doctor.especialidade,
            'profile_complete': bool(doctor.crm_medico and doctor.cns_medico)
        }