"""
Registration Service - Process and Patient Registration Business Logic

This service handles the complex business logic for registering processes and patients
in the database, including patient versioning, transaction management, and data validation.

Extracted from helpers.py to follow service-oriented architecture principles.
"""

import logging
from typing import List, Dict, Any, Optional
from django.db import transaction
from django.forms.models import model_to_dict

from processos.models import Processo, Doenca
from pacientes.models import Paciente
from clinicas.models import Emissor
from usuarios.models import Usuario

logger = logging.getLogger('processos.database')


class ProcessRegistrationService:
    """
    Service for handling process and patient registration business logic.
    
    This service encapsulates the complex workflow of:
    - Patient creation and versioning
    - Process registration and updates
    - Medication associations
    - Issuer relationships
    - Transaction management
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    @transaction.atomic
    def register_process(
        self,
        dados: Dict[str, Any],
        meds_ids: List[str],
        doenca: Doenca,
        emissor: Emissor,
        usuario: Usuario,
        paciente_existe: Optional[Paciente] = None,
        cid: Optional[str] = None,
        processo_id: Optional[int] = None
    ) -> int:
        """
        Registers a complete process with patient and medication data in the database.
        
        This method handles both creating new patients and updating existing ones,
        as well as creating and updating processes. It manages the complex business
        logic around patient versioning and process uniqueness constraints.
        
        Args:
            dados: Complete form data dictionary
            meds_ids: List of medication IDs to associate
            doenca: Disease instance for the process
            emissor: Issuer (doctor-clinic combination)
            usuario: User creating the process
            paciente_existe: Existing patient instance (if any)
            cid: Disease CID code (for new processes)
            processo_id: Process ID (for updates)
            
        Returns:
            int: The ID of the saved process
            
        Raises:
            ValueError: If required data is invalid or missing
            IntegrityError: If database constraints are violated
        """
        cpf_paciente = dados["cpf_paciente"]
        
        self.logger.info(f"register_process: Starting for CPF {cpf_paciente}, user {usuario.email}")
        self.logger.info(f"register_process: Patient exists: {bool(paciente_existe)}")
        self.logger.info(f"register_process: Disease: {doenca.cid} - {doenca.nome}")
        self.logger.info(f"register_process: Medications count: {len(meds_ids)}")
        
        if paciente_existe:
            return self._handle_existing_patient(
                dados, meds_ids, doenca, emissor, usuario, 
                paciente_existe, cid, processo_id
            )
        else:
            return self._handle_new_patient(
                dados, meds_ids, doenca, emissor, usuario
            )
    
    def _handle_existing_patient(
        self,
        dados: Dict[str, Any],
        meds_ids: List[str],
        doenca: Doenca,
        emissor: Emissor,
        usuario: Usuario,
        paciente_existe: Paciente,
        cid: Optional[str],
        processo_id: Optional[int]
    ) -> int:
        """Handle process registration for existing patient."""
        # Use versioned patient system - create or update version for this user
        versioned_patient = Paciente.create_or_update_for_user(
            usuario, self._extract_patient_data(dados)
        )
        
        # Generate process data
        dados_processo = self._generate_process_data(
            dados, meds_ids, doenca, emissor, versioned_patient, usuario
        )
        
        # Determine if process already exists
        processo_existe = False
        
        if processo_id:
            # Editing existing process
            processo_existe = True
            dados_processo["id"] = processo_id
        else:
            # Check for existing process with same patient-disease-user combination
            for p in paciente_existe.processos.all():
                if p.doenca.cid == cid and p.usuario == usuario:
                    processo_existe = True
                    dados_processo["id"] = p.id
                    break
        
        # Create and save process
        processo = self._prepare_model(Processo, **dados_processo)
        
        if processo_existe:
            processo.save(force_update=True)
        else:
            processo.save()
            # Increment user's process count for new processes
            usuario.process_count += 1
            usuario.save(update_fields=['process_count'])
        
        # Associate medications and issuer
        self._associate_medications(processo, meds_ids)
        emissor.pacientes.add(versioned_patient)
        
        return processo.pk
    
    def _handle_new_patient(
        self,
        dados: Dict[str, Any],
        meds_ids: List[str],
        doenca: Doenca,
        emissor: Emissor,
        usuario: Usuario
    ) -> int:
        """Handle process registration for new patient."""
        cpf_paciente = dados["cpf_paciente"]
        
        self.logger.info(f"register_process: Creating NEW patient for CPF {cpf_paciente}")
        
        try:
            # Create new patient with initial version
            self.logger.info("register_process: Creating patient with versioning")
            new_patient = Paciente.create_or_update_for_user(
                usuario, self._extract_patient_data(dados)
            )
            self.logger.info(f"register_process: New patient created with ID {new_patient.id}")
            
            # Generate process data
            self.logger.info("register_process: Generating process data")
            dados_processo = self._generate_process_data(
                dados, meds_ids, doenca, emissor, new_patient, usuario
            )
            
            # Create and save process
            self.logger.info("register_process: Creating process instance")
            processo = self._prepare_model(Processo, **dados_processo)
            
            try:
                processo.save()
                self.logger.info(f"register_process: Process saved with ID {processo.id}")
            except Exception as save_error:
                self.logger.error(f"register_process: CRITICAL ERROR saving process: {save_error}")
                self.logger.error(f"register_process: Process data: {dados_processo}")
                raise
            
            # Update user process count
            try:
                usuario.process_count += 1
                usuario.save(update_fields=['process_count'])
                self.logger.info(f"register_process: User process count updated to {usuario.process_count}")
            except Exception:
                self.logger.error("register_process: Error updating user process count")
                # Don't fail the whole transaction for this
            
            # Associate medications and issuer
            self.logger.info("register_process: Associating medications")
            self._associate_medications(processo, meds_ids)
            
            self.logger.info("register_process: Adding patient to emissor")
            emissor.pacientes.add(new_patient)
            
            return processo.pk
            
        except Exception as e:
            self.logger.error(f"register_process: CRITICAL ERROR in new patient creation: {e}")
            self.logger.error(f"register_process: Patient data: {self._extract_patient_data(dados)}")
            self.logger.error("register_process: Full traceback:", exc_info=True)
            raise
    
    def _extract_patient_data(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Extract patient-specific data from form data."""
        return {
            'nome_paciente': dados["nome_paciente"],
            'cpf_paciente': dados["cpf_paciente"],
            'peso': dados["peso"],
            'altura': dados["altura"],
            'nome_mae': dados["nome_mae"],
            'incapaz': dados["incapaz"],
            'nome_responsavel': dados["nome_responsavel"],
            'etnia': dados["etnia"],
            'telefone1_paciente': dados["telefone1_paciente"],
            'telefone2_paciente': dados["telefone2_paciente"],
            'email_paciente': dados["email_paciente"],
            'end_paciente': dados["end_paciente"],
        }
    
    def _generate_process_data(
        self,
        dados: Dict[str, Any],
        meds_ids: List[str],
        doenca: Doenca,
        emissor: Emissor,
        paciente: Paciente,
        usuario: Usuario
    ) -> Dict[str, Any]:
        """Generate process data dictionary from form data."""
        prescricao = self._generate_prescription_structure(meds_ids, dados)
        
        dados_processo = {
            'prescricao': prescricao,
            'anamnese': dados["anamnese"],
            'tratou': dados["tratou"],
            'tratamentos_previos': dados["tratamentos_previos"],
            'doenca': doenca,
            'preenchido_por': dados["preenchido_por"],
            'medico': emissor.medico,
            'paciente': paciente,
            'clinica': emissor.clinica,
            'emissor': emissor,
            'usuario': usuario,
            'dados_condicionais': {},
        }
        
        # Extract conditional data (fields starting with 'opt_')
        for key, value in dados.items():
            if key.startswith("opt_"):
                dados_processo["dados_condicionais"][key] = value
        
        return dados_processo
    
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
    
    def _generate_prescription_structure(self, meds_ids: List[str], form_data: Dict[str, Any]) -> Dict[str, Any]:
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
        logger.debug(f"ProcessRegistrationService: Generating prescription for {len(meds_ids)} medications")
        
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
        
        logger.debug(f"ProcessRegistrationService: Generated prescription structure with {len(prescricao)} medications")
        return prescricao