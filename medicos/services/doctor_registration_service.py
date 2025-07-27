"""
Doctor Registration Service - Doctor Registration Business Logic

This service handles the complex business logic for registering new doctors
and creating their accounts, including user creation, doctor profile creation,
and initial setup workflows.
"""

import logging
from typing import Dict, Any, Optional, Tuple
from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from medicos.repositories.doctor_repository import DoctorRepository

User = get_user_model()
logger = logging.getLogger('medicos.services')


class DoctorRegistrationService:
    """
    Service for handling doctor registration business logic.
    
    This service encapsulates the complex workflow of:
    - User account creation for doctors
    - Doctor profile creation and validation
    - Initial doctor setup workflows
    - Business rule validation for medical professionals
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.doctor_repository = DoctorRepository()
    
    @transaction.atomic
    def register_new_doctor(self, registration_data: Dict[str, Any]) -> Tuple[User, Any]:
        """
        Register a complete new doctor account with user and profile.
        
        This method handles the full registration workflow:
        1. Validate registration data
        2. Create user account
        3. Create doctor profile
        4. Set up initial doctor settings
        
        Args:
            registration_data: Complete registration form data
            
        Returns:
            Tuple[User, Medico]: Created user and doctor instances
            
        Raises:
            ValidationError: If registration data is invalid
            ValueError: If required data is missing
        """
        self.logger.info("DoctorRegistrationService: Starting new doctor registration")
        
        try:
            # Step 1: Validate registration data
            validation_errors = self._validate_registration_data(registration_data)
            if validation_errors:
                raise ValidationError(validation_errors)
            
            # Step 2: Create user account
            user = self._create_user_account(registration_data)
            self.logger.info(f"DoctorRegistrationService: Created user account for {user.email}")
            
            # Step 3: Create doctor profile
            doctor_data = self.doctor_repository.extract_doctor_data(registration_data)
            doctor = self.doctor_repository.create_doctor(user, doctor_data)
            self.logger.info(f"DoctorRegistrationService: Created doctor profile ID {doctor.id}")
            
            # Step 4: Set up initial doctor settings
            self._setup_initial_doctor_settings(user, doctor)
            
            self.logger.info(f"DoctorRegistrationService: Successfully registered doctor {doctor.nome_medico}")
            return user, doctor
            
        except Exception as e:
            self.logger.error(f"DoctorRegistrationService: Registration failed: {e}")
            raise
    
    def _create_user_account(self, registration_data: Dict[str, Any]) -> User:
        """
        Create a new user account for the doctor.
        
        Args:
            registration_data: Registration form data
            
        Returns:
            User: Created user instance
        """
        self.logger.debug("DoctorRegistrationService: Creating user account")
        
        # Extract user data
        user_data = {
            'email': registration_data['email'],
            'password': registration_data['password1'],
            'is_medico': True  # Mark as doctor account
        }
        
        # Create user
        user = User(email=user_data['email'], is_medico=user_data['is_medico'])
        user.set_password(user_data['password'])
        user.save()
        
        self.logger.debug(f"DoctorRegistrationService: Created user with email {user.email}")
        return user
    
    def _setup_initial_doctor_settings(self, user: User, doctor) -> None:
        """
        Set up initial settings and configurations for the new doctor.
        
        Args:
            user: The created user instance
            doctor: The created doctor instance
        """
        self.logger.debug(f"DoctorRegistrationService: Setting up initial settings for doctor {doctor.id}")
        
        # Set initial process count
        user.process_count = 0
        user.save(update_fields=['process_count'])
        
        # Any other initial setup can be added here
        # e.g., default notifications, initial onboarding flags, etc.
        
        self.logger.debug(f"DoctorRegistrationService: Initial setup complete for doctor {doctor.id}")
    
    def _validate_registration_data(self, registration_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate registration data for business rules.
        
        Args:
            registration_data: Form data to validate
            
        Returns:
            dict: Dictionary of validation errors (empty if valid)
        """
        self.logger.debug("DoctorRegistrationService: Validating registration data")
        
        errors = {}
        
        # Check required fields
        required_fields = ['email', 'password1', 'password2', 'nome']
        for field in required_fields:
            if not registration_data.get(field):
                errors[field] = f"{field} é obrigatório"
        
        # Password validation
        password1 = registration_data.get('password1')
        password2 = registration_data.get('password2')
        if password1 and password2 and password1 != password2:
            errors['password2'] = "As senhas não coincidem"
        
        # Email uniqueness check
        email = registration_data.get('email')
        if email and self.doctor_repository.check_email_exists(email):
            errors['email'] = "Este email já está cadastrado"
        
        # During initial registration, CRM and CNS are None
        # They will be added later during profile completion step
        
        error_count = len(errors)
        self.logger.debug(f"DoctorRegistrationService: Validation completed with {error_count} errors")
        
        return errors
    
    def check_registration_eligibility(self, email: str) -> Dict[str, Any]:
        """
        Check if an email is eligible for doctor registration.
        
        Args:
            email: Email to check
            
        Returns:
            dict: Eligibility information with status and details
        """
        self.logger.debug(f"DoctorRegistrationService: Checking eligibility for {email}")
        
        result = {
            'eligible': True,
            'reasons': []
        }
        
        # Check if email already exists
        if self.doctor_repository.check_email_exists(email):
            result['eligible'] = False
            result['reasons'].append('Email já cadastrado no sistema')
        
        # Check if email domain is allowed (if you have domain restrictions)
        # This could be extended for institutional email validation
        
        self.logger.debug(f"DoctorRegistrationService: Eligibility check result: {result['eligible']}")
        return result