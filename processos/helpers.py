"""
Helper Functions - Backward Compatibility Facade

This module serves as a backward compatibility layer while the codebase transitions
to the new service-oriented architecture. It provides import facades for existing
code that still uses the old helper function interfaces.

MIGRATION NOTES:
- This file maintains compatibility during the transition period
- New code should use the service/repository/utils modules directly
- This facade will be gradually deprecated as imports are updated

Architecture Mapping:
- Complex business logic → services/
- Data access patterns → repositories/  
- Pure utilities → utils/
"""

import logging
from datetime import datetime
from django.forms.models import model_to_dict

# Import the new architecture components
from processos.services.registration_service import ProcessRegistrationService
from processos.services.prescription_data_service import PrescriptionDataService
from processos.repositories.patient_repository import PatientRepository
from processos.repositories.medication_repository import MedicationRepository
from processos.utils.model_utils import prepare_model
from processos.utils.data_utils import link_issuer_data
from processos.utils.url_utils import generate_protocol_link

logger = logging.getLogger(__name__)


# =============================================================================
# BACKWARD COMPATIBILITY FACADES
# =============================================================================

# Service instances for facade functions
_registration_service = ProcessRegistrationService()
_prescription_data_service = PrescriptionDataService()
_patient_repository = PatientRepository()
_medication_repository = MedicationRepository()


# MODEL UTILITIES FACADE
def preparar_modelo(modelo, **kwargs):
    """
    LEGACY FACADE: Use processos.utils.model_utils.prepare_model instead.
    """
    return prepare_model(modelo, **kwargs)


# PATIENT REPOSITORY FACADE
def checar_paciente_existe(cpf_paciente):
    """
    LEGACY FACADE: Use processos.repositories.patient_repository.PatientRepository.check_patient_exists instead.
    """
    return _patient_repository.check_patient_exists(cpf_paciente)


def gerar_dados_paciente(dados):
    """
    LEGACY FACADE: Use processos.repositories.patient_repository.PatientRepository.extract_patient_data instead.
    """
    return _patient_repository.extract_patient_data(dados)


# MEDICATION REPOSITORY FACADE
def listar_med(cid):
    """
    LEGACY FACADE: Use processos.repositories.medication_repository.MedicationRepository.list_medications_by_cid instead.
    """
    return _medication_repository.list_medications_by_cid(cid)


def gera_med_dosagem(dados_formulario, ids_med_formulario):
    """
    LEGACY FACADE: Use processos.repositories.medication_repository.MedicationRepository.format_medication_dosages instead.
    """
    return _medication_repository.format_medication_dosages(dados_formulario, ids_med_formulario)


def associar_med(processo, meds):
    """
    LEGACY FACADE: Use processos.repositories.medication_repository.MedicationRepository.associate_medications_with_process instead.
    """
    return _medication_repository.associate_medications_with_process(processo, meds)


def gerar_lista_meds_ids(dados):
    """
    LEGACY FACADE: Use processos.repositories.medication_repository.MedicationRepository.extract_medication_ids_from_form instead.
    """
    return _medication_repository.extract_medication_ids_from_form(dados)


# PRESCRIPTION DATA SERVICE FACADE
def resgatar_prescricao(dados, processo):
    """
    LEGACY FACADE: Use processos.services.prescription_data_service.PrescriptionDataService.retrieve_prescription_data instead.
    """
    return _prescription_data_service.retrieve_prescription_data(dados, processo)


def gerar_prescricao(meds_ids, dados_formulario):
    """
    LEGACY FACADE: Use processos.services.prescription_data_service.PrescriptionDataService.generate_prescription_structure instead.
    """
    return _prescription_data_service.generate_prescription_structure(meds_ids, dados_formulario)


def gerar_dados_processo(dados, meds_ids, doenca, emissor, paciente, usuario):
    """
    LEGACY FACADE: Use processos.services.prescription_data_service.PrescriptionDataService.generate_process_data instead.
    """
    return _prescription_data_service.generate_process_data(dados, meds_ids, doenca, emissor, paciente, usuario)


def gerar_dados_edicao_parcial(dados, processo_id):
    """
    LEGACY FACADE: Use processos.services.prescription_data_service.PrescriptionDataService.extract_partial_edit_data instead.
    """
    return _prescription_data_service.extract_partial_edit_data(dados, processo_id)


# DATA UTILITIES FACADE
def vincula_dados_emissor(usuario, medico, clinica, dados_formulario):
    """
    LEGACY FACADE: Use processos.utils.data_utils.link_issuer_data instead.
    """
    return link_issuer_data(usuario, medico, clinica, dados_formulario)


# URL UTILITIES FACADE
def gerar_link_protocolo(cid):
    """
    LEGACY FACADE: Use processos.utils.url_utils.generate_protocol_link instead.
    """
    return generate_protocol_link(cid)


# REGISTRATION SERVICE FACADE
def registrar_db(dados, meds_ids, doenca, emissor, usuario, **kwargs):
    """
    LEGACY FACADE: Use processos.services.registration_service.ProcessRegistrationService.register_process instead.
    """
    return _registration_service.register_process(
        dados=dados,
        meds_ids=meds_ids,
        doenca=doenca,
        emissor=emissor,
        usuario=usuario,
        **kwargs
    )


# RENEWAL SERVICE FACADE (delegated to existing enhanced service)
def cria_dict_renovação(modelo, user=None):
    """
    LEGACY FACADE: Use processos.prescription_services.RenewalService.create_renewal_dictionary instead.
    """
    from processos.services.prescription_services import RenewalService
    renewal_service = RenewalService()
    return renewal_service.create_renewal_dictionary(modelo, user)


def gerar_dados_renovacao(primeira_data, processo_id, user=None):
    """
    LEGACY FACADE: Use processos.prescription_services.RenewalService.generate_renewal_data instead.
    """
    from processos.services.prescription_services import RenewalService
    renewal_service = RenewalService()
    return renewal_service.generate_renewal_data(primeira_data, processo_id, user)


# LEGACY PDF COORDINATION (maintained for compatibility)
def transfere_dados_gerador(dados):
    """
    Legacy PDF generation coordination function.
    
    This function maintains backward compatibility while using the new
    service architecture. It delegates to the appropriate services for
    PDF generation and file handling.
    
    Args:
        dados (dict): Complete data dictionary for the process
        
    Returns:
        str: Path to the generated PDF file, or None if error occurs
    """
    try:
        from analytics.signals import track_pdf_generation
        
        pdf_logger = logging.getLogger('processos.pdf')
        pdf_logger.info("transfere_dados_gerador: Starting with new service architecture")
        
        # Save identifiers before PDF generation
        cpf_paciente = dados.get('cpf_paciente', 'unknown')
        cid = dados.get('cid', 'unknown')
        
        # Use new PrescriptionPDFService for PDF generation
        from processos.services.prescription_services import PrescriptionPDFService
        pdf_service = PrescriptionPDFService()
        
        # Generate PDF using the service
        user = dados.get('usuario')
        response = pdf_service.generate_prescription_pdf(dados, user=user)
        
        if response is None:
            pdf_logger.error("transfere_dados_gerador: PDF generation returned None")
            return None
        
        # Use I/O service for file operations
        from processos.services.io_services import PDFFileService
        file_service = PDFFileService()
        return file_service.save_pdf_and_get_url(response, cpf_paciente, cid)
        
    except Exception as e:
        pdf_logger.error(f"Exception in transfere_dados_gerador: {e}", exc_info=True)
        return None


# =============================================================================
# MIGRATION GUIDANCE
# =============================================================================

def _log_migration_warning(old_function: str, new_path: str):
    """Log migration guidance for developers."""
    logger.warning(
        f"MIGRATION: {old_function} is deprecated. "
        f"Use {new_path} instead. "
        f"See architecture documentation for details."
    )


# Add migration warnings for key functions (can be enabled during development)
def _enable_migration_warnings():
    """Enable migration warnings for development (call this in development settings)."""
    import functools
    
    # Wrap facade functions with migration warnings
    global registrar_db, listar_med, checar_paciente_existe
    
    original_registrar_db = registrar_db
    @functools.wraps(original_registrar_db)
    def registrar_db_with_warning(*args, **kwargs):
        _log_migration_warning(
            'registrar_db', 
            'processos.services.registration_service.ProcessRegistrationService.register_process'
        )
        return original_registrar_db(*args, **kwargs)
    
    registrar_db = registrar_db_with_warning
    
    # Add similar wrappers for other key functions as needed