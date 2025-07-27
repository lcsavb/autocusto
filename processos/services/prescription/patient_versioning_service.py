"""
Patient Versioning Service - Single Responsibility: Patient Versioning

This service handles ONLY patient versioning operations.
It encapsulates the complex patient versioning business logic that ensures
each user gets their own version of patient data.

Single Responsibility:
- Patient versioning creation and updates
- User-specific patient data access

Does NOT handle:
- Process operations (that's ProcessRepository)
- User statistics (that's UserStatisticsService)
- Medication associations (that's ProcessMedicationService)
- Database CRUD beyond patient versioning
"""

import logging
from typing import Dict, Any
from django.db import transaction

from pacientes.models import Paciente
from usuarios.models import Usuario

logger = logging.getLogger('processos.patient_versioning')


class PatientVersioningService:
    """
    Service for patient versioning operations.
    
    This service implements the patient versioning system where each user
    gets their own version of patient data for data privacy and isolation.
    
    Responsibilities:
    - Create or update patient versions for users
    - Retrieve user-specific patient data
    - Handle patient versioning business rules
    
    Does NOT handle other business logic outside of patient versioning.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    @transaction.atomic  # LGPD compliance: Ensures user isolation atomicity
    def create_or_update_patient_for_user(
        self, 
        usuario: Usuario, 
        patient_data: Dict[str, Any]
    ) -> Paciente:
        """
        Create or update a patient version for a specific user.
        
        Privacy-by-design versioning system: Each user gets isolated patient data copy
        to comply with Brazilian LGPD (Lei Geral de Proteção de Dados). This prevents
        cross-contamination of patient data between medical professionals while
        maintaining audit trail integrity.
        
        Smart versioning: Only creates new versions when data actually changes,
        preventing database bloat while preserving complete change history.
        
        Args:
            usuario: The user who will own this patient version
            patient_data: Dictionary containing patient data fields
            
        Returns:
            Paciente: The versioned patient instance for this user
            
        Raises:
            ValueError: If patient data is invalid
            IntegrityError: If database constraints are violated
        """
        cpf = patient_data.get('cpf_paciente')
        self.logger.info(f"PatientVersioning: Creating/updating patient for user {usuario.email}, CPF {cpf}")
        
        if not cpf:
            raise ValueError("CPF is required for patient versioning")
        
        # Smart versioning: Reuse existing version if data hasn't changed (prevents bloat)
        existing_patient = self._user_has_version_with_same_data(usuario, patient_data)
        if existing_patient:
            self.logger.info(f"PatientVersioning: No data changes, reusing existing patient ID: {existing_patient.id}")
            return existing_patient
        
        # Create new version for audit compliance - preserves complete change history
        self.logger.info(f"PatientVersioning: Creating new version (data changed or first version)")
        versioned_patient = Paciente.create_or_update_for_user(usuario, patient_data)
        
        self.logger.info(f"PatientVersioning: Patient versioning completed, patient ID: {versioned_patient.id}")
        return versioned_patient
    
    def get_patient_version_for_user(self, cpf: str, usuario: Usuario) -> Paciente:
        """
        Get user's isolated patient version - enforces privacy boundaries.
        
        LGPD compliance: Each user only sees their own patient data version,
        preventing unauthorized access to patient information across medical professionals.
        
        Args:
            cpf: The patient's CPF
            usuario: The user requesting access
            
        Returns:
            Paciente: The patient version for this user
            
        Raises:
            Paciente.DoesNotExist: If no version exists for this user
        """
        self.logger.debug(f"PatientVersioning: Getting patient version for user {usuario.email}, CPF {cpf}")
        
        # This would use the patient versioning system to get the user's version
        # Implementation depends on the specific versioning model
        try:
            patient = Paciente.objects.get(cpf_paciente=cpf)
            # Privacy enforcement: Only return user's own version, never another user's data
            user_version = patient.get_version_for_user(usuario)
            
            if user_version:
                self.logger.debug(f"PatientVersioning: Found version for user {usuario.email}")
                return user_version
            else:
                self.logger.warning(f"PatientVersioning: No version found for user {usuario.email}")
                raise Paciente.DoesNotExist(f"No patient version for user {usuario.email}")
                
        except Paciente.DoesNotExist:
            self.logger.warning(f"PatientVersioning: Patient with CPF {cpf} not found")
            raise
    
    def check_user_has_patient_access(self, patient: Paciente, usuario: Usuario) -> bool:
        """
        Check if a user has access to a patient through versioning.
        
        Args:
            patient: The patient instance
            usuario: The user to check access for
            
        Returns:
            bool: True if user has access through versioning
        """
        self.logger.debug(f"PatientVersioning: Checking access for user {usuario.email}, patient {patient.id}")
        
        try:
            version = patient.get_version_for_user(usuario)
            has_access = version is not None
            self.logger.debug(f"PatientVersioning: User access check result: {has_access}")
            return has_access
        except Exception as e:
            self.logger.error(f"PatientVersioning: Error checking access: {e}")
            return False
    
    def _user_has_version_with_same_data(self, usuario: Usuario, patient_data: Dict[str, Any]):
        """
        Check if user already has a version with the same data.
        
        Returns:
            Paciente: existing patient if data is identical, None otherwise
        """
        cpf = patient_data.get('cpf_paciente')
        
        try:
            from ...repositories.patient_repository import PatientRepository
            patient_repo = PatientRepository()
            existing_patient = patient_repo.check_patient_exists(cpf)
            
            if not existing_patient:  # Returns False if patient doesn't exist
                self.logger.debug(f"PatientVersioning: Patient with CPF {cpf} does not exist")
                return None
                
            existing_version = existing_patient.get_version_for_user(usuario)
            
            if not existing_version:
                return None
            
            # Versioning fields: Only track medically relevant changes to prevent bloat
            version_fields = [
                'nome_paciente', 'nome_mae', 'peso', 'altura', 'end_paciente',
                'incapaz', 'nome_responsavel', 'etnia', 'telefone1_paciente',
                'telefone2_paciente', 'email_paciente'
            ]
            
            # Smart comparison: Detect actual data changes vs cosmetic differences (whitespace)
            changed_fields = [
                field for field in version_fields
                if str(getattr(existing_version, field, '') or '').strip() != str(patient_data.get(field, '') or '').strip()
            ]
            
            if changed_fields:
                self.logger.debug(f"PatientVersioning: Changed fields: {changed_fields}")
                return None
            
            self.logger.debug(f"PatientVersioning: All fields identical")
            return existing_patient
            
        except Exception as e:
            self.logger.error(f"PatientVersioning: Unexpected error checking version for CPF {cpf}: {e}")
            raise  # Don't mask unexpected errors