"""
Prescription Database Service - Database Operations for Prescriptions

This service handles ALL database operations and business logic for prescriptions.
It is called ONLY by Django forms through their save() methods, maintaining
proper Django patterns where forms handle database operations.

Responsibilities:
- Patient versioning and creation/update
- Process creation and updates with business rules
- Medication associations and relationship management
- User statistics updates
- Complex business logic that forms need

This service is the ONLY path to database operations for prescription processes.
Views should NEVER call this service directly - only through forms.
"""

import logging
from typing import List, Dict, Any, Optional
from django.db import transaction
from django.forms.models import model_to_dict

from processos.models import Processo, Doenca
from pacientes.models import Paciente
from clinicas.models import Emissor
from usuarios.models import Usuario
from .data_builder import PrescriptionDataBuilder
from .patient_versioning_service import PatientVersioningService

logger = logging.getLogger('processos.database')


class ProcessRepository:
    """
    Service for database operations and business logic for prescriptions.
    
    Responsibilities (DATABASE & BUSINESS LOGIC):
    - Patient versioning and creation/updates
    - Process creation and updates with business rules
    - Medication associations and relationship management  
    - User statistics and count updates
    - Complex business logic that Django forms need
    
    This service is called ONLY by Django forms via their save() methods.
    Views should NEVER call this service directly.
    
    Does NOT handle:
    - Data construction (that's PrescriptionDataService)
    - PDF generation
    - File operations
    - HTTP responses
    - Raw form validation
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_builder = PrescriptionDataBuilder()
        self.patient_versioning = PatientVersioningService()
    
    # Clean Repository Interface Methods (accepts structured data only)
    
    @transaction.atomic
    def create_process_from_structured_data(self, structured_data: Dict[str, Any]) -> int:
        """
        Create new process from pre-structured data.
        
        This is the NEW clean interface that accepts only structured data from DataBuilder.
        
        Args:
            structured_data: Output from PrescriptionDataBuilder.build_prescription_data()
                {
                    'patient_data': {...},
                    'process_data': {...}, 
                    'medication_ids': [...],
                    'metadata': {...}
                }
        Returns:
            int: Created process ID
        """
        patient_data = structured_data['patient_data']
        process_data = structured_data['process_data'] 
        medication_ids = structured_data['medication_ids']
        metadata = structured_data['metadata']
        
        self.logger.info(f"ProcessRepository: Creating process from structured data")
        self.logger.info(f"ProcessRepository: Patient exists: {metadata['patient_exists']}")
        self.logger.info(f"ProcessRepository: Medications count: {len(medication_ids)}")
        
        if metadata['patient_exists']:
            return self._create_with_existing_patient(patient_data, process_data, medication_ids, metadata)
        else:
            return self._create_with_new_patient(patient_data, process_data, medication_ids, metadata)
    
    @transaction.atomic
    def update_process_from_structured_data(self, process_id: int, structured_data: Dict[str, Any]) -> int:
        """
        Update existing process from pre-structured data.
        
        Args:
            process_id: ID of process to update
            structured_data: Output from PrescriptionDataBuilder.build_prescription_data()
            
        Returns:
            int: Updated process ID
        """
        patient_data = structured_data['patient_data']
        process_data = structured_data['process_data'] 
        medication_ids = structured_data['medication_ids']
        metadata = structured_data['metadata']
        
        self.logger.info(f"ProcessRepository: Updating process {process_id} from structured data")
        
        # Set the process ID in process_data for update
        process_data['id'] = process_id
        
        return self._update_existing_process(process_id, patient_data, process_data, medication_ids, metadata)
    
    def _create_with_existing_patient(self, patient_data: Dict, process_data: Dict, medication_ids: List[str], metadata: Dict) -> int:
        """Create process with existing patient using structured data."""
        # Use patient versioning service
        versioned_patient = self.patient_versioning.create_or_update_patient_for_user(
            process_data['usuario'], patient_data
        )
        
        # Set the patient in process data
        process_data['paciente'] = versioned_patient
        
        # Check if process already exists
        existing_process = self.check_existing_process(
            metadata.get('existing_patient'), metadata.get('cid'), process_data['usuario']
        )
        
        # Create process
        processo = self._prepare_model(Processo, **process_data)
        
        if existing_process:
            processo.id = existing_process.id
            processo.save(force_update=True)
        else:
            processo.save()
            # Increment user count for new processes
            if self.should_increment_user_count(existing_process):
                process_data['usuario'].process_count += 1
                process_data['usuario'].save(update_fields=['process_count'])
        
        # Associate medications and issuer
        self._associate_medications(processo, medication_ids)
        process_data['emissor'].pacientes.add(versioned_patient)
        
        return processo.pk
    
    def _create_with_new_patient(self, patient_data: Dict, process_data: Dict, medication_ids: List[str], metadata: Dict) -> int:
        """Create process with new patient using structured data."""
        # Use patient versioning service
        new_patient = self.patient_versioning.create_or_update_patient_for_user(
            process_data['usuario'], patient_data
        )
        
        # Set the patient in process data
        process_data['paciente'] = new_patient
        
        # Create process
        processo = self._prepare_model(Processo, **process_data)
        processo.save()
        
        # Update user process count
        process_data['usuario'].process_count += 1
        process_data['usuario'].save(update_fields=['process_count'])
        
        # Associate medications and issuer
        self._associate_medications(processo, medication_ids)
        process_data['emissor'].pacientes.add(new_patient)
        
        return processo.pk
    
    def _update_existing_process(self, process_id: int, patient_data: Dict, process_data: Dict, medication_ids: List[str], metadata: Dict) -> int:
        """Update existing process using structured data."""
        # Update patient data if needed using versioning service
        if metadata['patient_exists']:
            versioned_patient = self.patient_versioning.create_or_update_patient_for_user(
                process_data['usuario'], patient_data
            )
            process_data['paciente'] = versioned_patient
        
        # Update process
        processo = self._prepare_model(Processo, **process_data)
        processo.save(force_update=True)
        
        # Update medication associations
        self._associate_medications(processo, medication_ids)
        
        return processo.pk

    # Database Operations and Business Logic Methods (for Django forms to use)
    
    # REMOVED: handle_patient_versioning() - Use PatientVersioningService directly instead
    
    def check_existing_process(self, paciente_existe: Optional[Paciente], cid: str, usuario: Usuario) -> Optional[Processo]:
        """
        Check if process already exists for patient-disease-user combination.
        
        Business rule: prevent duplicate processes for same patient, disease, and user.
        Forms should call this to determine if they're updating or creating.
        
        Args:
            paciente_existe: Existing patient instance (if any)
            cid: Disease CID code
            usuario: User creating the process
            
        Returns:
            Optional[Processo]: Existing process if found, None for new creation
        """
        if not paciente_existe or not cid:
            return None
            
        self.logger.info(f"BusinessLogic: Checking existing process - Patient: {paciente_existe.id}, CID: {cid}")
        
        for processo in paciente_existe.processos.all():
            if processo.doenca.cid == cid and processo.usuario == usuario:
                self.logger.info(f"BusinessLogic: Found existing process ID: {processo.id}")
                return processo
        
        self.logger.info("BusinessLogic: No existing process found")
        return None
    
    def should_increment_user_count(self, existing_process: Optional[Processo]) -> bool:
        """
        Determine if user process count should be incremented.
        
        Business rule: only increment count for new processes, not updates.
        
        Args:
            existing_process: Existing process if found
            
        Returns:
            bool: True if count should be incremented
        """
        should_increment = existing_process is None
        self.logger.info(f"BusinessLogic: Should increment user count: {should_increment}")
        return should_increment
    
    def get_medication_changes(self, processo: Processo, new_medication_ids: List[str]) -> Dict[str, List[str]]:
        """
        Determine medication changes for process update.
        
        Business logic: calculate which medications to add and remove.
        
        Args:
            processo: Process instance
            new_medication_ids: New list of medication IDs
            
        Returns:
            Dict with 'add' and 'remove' lists
        """
        current_med_ids = [str(med.id) for med in processo.medicamentos.all()]
        
        to_add = [med_id for med_id in new_medication_ids if med_id not in current_med_ids]
        to_remove = [med_id for med_id in current_med_ids if med_id not in new_medication_ids]
        
        self.logger.info(f"BusinessLogic: Medication changes - Add: {len(to_add)}, Remove: {len(to_remove)}")
        
        return {
            'add': to_add,
            'remove': to_remove
        }
    
    def get_process_by_id_and_user(self, process_id: int, user) -> 'Processo':
        """
        Get process by ID ensuring user ownership.
        
        Args:
            process_id: Process ID to retrieve
            user: User who must own the process
            
        Returns:
            Processo: The process instance
            
        Raises:
            Processo.DoesNotExist: If process not found or not owned by user
        """
        from processos.models import Processo
        self.logger.debug(f"ProcessRepository: Getting process {process_id} for user {user.email}")
        
        try:
            processo = Processo.objects.get(id=process_id, usuario=user)
            self.logger.debug(f"ProcessRepository: Found process {process_id}")
            return processo
        except Processo.DoesNotExist:
            self.logger.error(f"ProcessRepository: Process {process_id} not found for user {user.email}")
            raise
    
    def _prepare_model(self, modelo, **kwargs):
        """
        Prepare a Django model instance from a dictionary of data.
        
        This is a utility method that creates a model instance with the provided data.
        """
        return modelo(**kwargs)
    
    def _associate_medications(self, processo: Processo, meds_ids: List[str]) -> None:
        """
        Associate medications with a process, synchronizing the relationship.
        
        This method ensures that the medications linked to a process match
        the provided list of medication IDs.
        """
        # Add new medications
        for med_id in meds_ids:
            processo.medicamentos.add(med_id)
        
        # Remove medications not in the new list
        current_meds = processo.medicamentos.all()
        for med_cadastrado in current_meds:
            if str(med_cadastrado.id) not in meds_ids:
                processo.medicamentos.remove(med_cadastrado)
    
    def update_process_date_only(self, process_id: int, new_date: str, medication_ids: List[str]) -> None:
        """
        Update only the date in a process (quick renewal functionality).
        
        Args:
            process_id: Process ID to update
            new_date: New date for the prescription
            medication_ids: List of medication IDs to associate
        """
        from django.core.serializers.json import DjangoJSONEncoder
        import json
        
        self.logger.info(f"ProcessRepository: Quick date update for process {process_id}")
        
        processo = Processo.objects.get(id=process_id)
        processo.prescricao['1']['data_1'] = new_date
        
        # Ensure proper JSON serialization with Django's encoder
        processo.prescricao = json.loads(json.dumps(processo.prescricao, cls=DjangoJSONEncoder))
        processo.save(update_fields=['prescricao'])
        
        # Update medication associations
        self._associate_medications(processo, medication_ids)
    
