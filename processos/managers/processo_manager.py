"""
Processo Model Manager - Database Operations Only

This manager handles complex database operations for Processo model
following Django patterns. It does NOT contain business logic.
"""

from django.db import models
from django.db import transaction


class ProcessoManager(models.Manager):
    """
    Custom manager for Processo model handling database operations.
    
    Responsibilities (DATABASE OPERATIONS ONLY):
    - Complex database queries
    - Model creation with relationships
    - Database-level constraints and validations
    - Transaction management for model operations
    
    Does NOT handle:
    - Business logic (versioning, duplication rules)
    - Data transformation/construction
    - Business rule validation
    """
    
    @transaction.atomic
    def create_prescription_process(
        self,
        process_data: dict,
        patient,
        medications_ids: list,
        is_update: bool = False,
        process_id: int = None
    ):
        """
        Create or update a prescription process with all relationships.
        
        This method handles ONLY database operations:
        - Creating/updating Processo instance
        - Setting up medication relationships
        - Managing foreign key relationships
        - Ensuring data integrity
        
        Args:
            process_data: Clean process data dict (no business logic applied)
            patient: Patient instance (already versioned by business logic)
            medications_ids: List of medication IDs to associate
            is_update: Whether this is an update operation
            process_id: Process ID for updates
            
        Returns:
            Processo: The created or updated process instance
        """
        if is_update and process_id:
            # Update existing process
            processo = self.get(id=process_id)
            for field, value in process_data.items():
                setattr(processo, field, value)
            processo.save()
        else:
            # Create new process
            processo = self.create(**process_data)
        
        # Handle medication relationships
        self._sync_medications(processo, medications_ids)
        
        return processo
    
    def _sync_medications(self, processo, medication_ids: list):
        """
        Synchronize medication relationships for a process.
        
        This is a pure database operation that ensures the medication
        relationships match the provided list.
        """
        # Clear existing relationships
        processo.medicamentos.clear()
        
        # Add new relationships
        for med_id in medication_ids:
            processo.medicamentos.add(med_id)
    
    def get_process_for_patient_and_disease(self, patient, disease_cid, user):
        """
        Database query to find existing process for patient/disease/user combination.
        
        This is a pure query method with no business logic.
        """
        return self.filter(
            paciente=patient,
            doenca__cid=disease_cid,
            usuario=user
        ).first()
    
    def get_user_processes_with_related(self, user):
        """
        Optimized query for user processes with related data.
        
        Pure database optimization - no business logic.
        """
        return self.filter(usuario=user).select_related(
            'paciente', 'doenca', 'medico', 'clinica'
        ).prefetch_related('medicamentos')
EOF < /dev/null