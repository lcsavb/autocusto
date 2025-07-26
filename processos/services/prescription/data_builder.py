"""
Prescription Data Service - Pure Data Construction

This service handles ONLY data construction and transformation from form data.
It does NOT perform any database operations - that's handled by PrescriptionDatabaseService.

Responsibilities:
- Extract and format patient data from forms
- Construct complex prescription data structures (6-month schedules)
- Assemble complete process data with all components
- Prepare structured data for database operations

Does NOT handle:
- Database operations (that's PrescriptionDatabaseService)
- Business logic decisions (that's PrescriptionDatabaseService)
- PDF generation
- File operations
- HTTP responses
- Raw form validation
"""

import logging
from typing import List, Dict, Any, Optional

from processos.models import Doenca
from clinicas.models import Emissor
from usuarios.models import Usuario
from pacientes.models import Paciente

logger = logging.getLogger('processos.data')


class PrescriptionDataBuilder:
    """
    Service for pure data construction from form data.
    
    This service transforms raw form data into structured objects
    ready for database operations, but performs NO database operations itself.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def build_prescription_data(
        self,
        dados: Dict[str, Any],
        meds_ids: List[str],
        doenca: Doenca,
        emissor: Emissor,
        usuario: Usuario,
        paciente_existe: Optional[Paciente] = None,
        cid: Optional[str] = None,
        processo_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Constructs complete prescription data from form data (NO DATABASE OPERATIONS).
        
        This method builds all necessary data structures for a prescription process
        but does NOT save anything to the database. Returns structured data that 
        PrescriptionDatabaseService can use for database operations.
        
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
            Dict containing all structured data needed for database operations:
            {
                'patient_data': {...},
                'process_data': {...},
                'medication_ids': [...],
                'metadata': {...}
            }
        """
        cpf_paciente = dados["cpf_paciente"]
        
        self.logger.info(f"DataConstruction: Building prescription data for CPF {cpf_paciente}, user {usuario.email}")
        self.logger.info(f"DataConstruction: Disease: {doenca.cid} - {doenca.nome}")
        self.logger.info(f"DataConstruction: Medications count: {len(meds_ids)}")
        
        # Extract patient data
        patient_data = self.extract_patient_data(dados)
        
        # Build prescription structure  
        prescription_structure = self.build_prescription_structure(meds_ids, dados)
        
        # Generate process data (without database models)
        process_data = {
            'prescricao': prescription_structure,
            'anamnese': dados["anamnese"],
            'tratou': dados["tratou"],
            'tratamentos_previos': dados["tratamentos_previos"],
            'doenca': doenca,
            'preenchido_por': dados["preenchido_por"],
            'medico': emissor.medico,
            'clinica': emissor.clinica,
            'emissor': emissor,
            'usuario': usuario,
            'dados_condicionais': {},
        }
        
        # Extract conditional data (fields starting with 'opt_')
        for key, value in dados.items():
            if key.startswith("opt_"):
                process_data["dados_condicionais"][key] = value
        
        # Metadata for database operations
        metadata = {
            'patient_exists': bool(paciente_existe),
            'existing_patient': paciente_existe,
            'cid': cid,
            'process_id': processo_id,
            'is_update': bool(processo_id),
        }
        
        self.logger.info("DataConstruction: Prescription data construction completed")
        
        return {
            'patient_data': patient_data,
            'process_data': process_data,
            'medication_ids': meds_ids,
            'metadata': metadata
        }
    
    def extract_patient_data(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract patient-specific data from form data.
        
        Pure data extraction with no business logic or database operations.
        
        Args:
            dados: Complete form data dictionary
            
        Returns:
            Dict: Patient data ready for database operations
        """
        patient_data = {
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
        
        self.logger.debug(f"DataConstruction: Extracted patient data for CPF {patient_data['cpf_paciente']}")
        return patient_data
    
    def build_prescription_structure(self, meds_ids: List[str], form_data: Dict[str, Any]) -> Dict[str, Any]:
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
        self.logger.debug(f"DataConstruction: Building prescription structure for {len(meds_ids)} medications")
        
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
        
        self.logger.debug(f"DataConstruction: Generated prescription structure with {len(prescricao)} medications")
        return prescricao