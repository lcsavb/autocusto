"""
View Services - Setup and Data Preparation for Views

This module provides services that handle the complex setup logic for prescription views.
These services extract the heavy lifting from views, making them thin controllers that
focus only on HTTP concerns.

Services:
- PrescriptionViewSetupService: Handles all setup logic for prescription views
"""

import logging
from typing import Optional, List, Tuple, Any, Union
from datetime import date

from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import QuerySet

from medicos.seletor import medico as seletor_medico
from processos.models import Processo, Doenca
from processos.repositories.medication_repository import MedicationRepository
from processos.services.prescription_services import RenewalService
from processos.forms import fabricar_formulario
from processos.views import _get_initial_data
from processos.services.view_setup_models import (
    ViewSetupResult, SetupError, ViewSetupSuccess,
    CommonSetupData, PrescriptionFormData, 
    NewPrescriptionData, EditPrescriptionData,
    is_setup_error, is_setup_success
)


logger = logging.getLogger(__name__)


class PrescriptionViewSetupService:
    """
    Service for setting up prescription views (cadastro and edicao).
    
    Handles all the complex setup logic that views currently do:
    - User and doctor validation
    - Session state validation
    - Clinic choices preparation
    - Dynamic form construction
    - Initial data preparation
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def setup_for_new_prescription(self, request) -> ViewSetupResult:
        """
        Set up all data needed for the cadastro (new prescription) view.
        
        Args:
            request: Django HTTP request object
            
        Returns:
            ViewSetupResult: Contains all setup data or error information
        """
        try:
            print(f"DEBUG SETUP: ============= SETUP SERVICE CALLED =============")
            print(f"DEBUG SETUP: Starting setup_for_new_prescription for user: {request.user}")
            self.logger.info(f"Setting up new prescription view for user: {request.user}")
            
            # Step 1: Common setup (user, doctor, clinics)
            print(f"DEBUG SETUP: Calling _setup_common_data")
            common_result = self._setup_common_data(request)
            print(f"DEBUG SETUP: Common setup result: {type(common_result)}")
            if isinstance(common_result, SetupError):
                return common_result
            
            # Step 2: Validate new prescription session requirements
            session_error = self._validate_new_prescription_session(request)
            if session_error:
                return session_error
            
            # Step 3: Get prescription-specific data
            paciente_existe = request.session["paciente_existe"]
            primeira_data = date.today().strftime("%d/%m/%Y")
            cid = request.session["cid"]
            
            # Step 4: Get medications and form for new prescription
            med_repo = MedicationRepository()
            medicamentos = med_repo.list_medications_by_cid(cid)
            ModeloFormulario = fabricar_formulario(cid, False)  # False = new prescription
            
            # Step 5: Prepare initial data based on patient existence
            try:
                dados_iniciais = _get_initial_data(request, paciente_existe, primeira_data, cid)
            except KeyError as e:
                self.logger.error(f"Missing session data for initial data: {e}")
                return SetupError(
                    message=str(e),
                    redirect_to="home"
                )
            
            self.logger.info(f"Successfully set up new prescription view for CID: {cid}")
            
            return ViewSetupSuccess(
                common=common_result,
                form=PrescriptionFormData(
                    cid=cid,
                    medicamentos=medicamentos,
                    ModeloFormulario=ModeloFormulario
                ),
                specific=NewPrescriptionData(
                    paciente_existe=paciente_existe,
                    primeira_data=primeira_data,
                    dados_iniciais=dados_iniciais
                )
            )
            
        except Exception as e:
            self.logger.error(f"Error setting up new prescription view: {e}", exc_info=True)
            return SetupError(
                message=f"Erro ao carregar dados do cadastro: {e}",
                redirect_to="home"
            )
    
    def setup_for_edit_prescription(self, request) -> ViewSetupResult:
        """
        Set up all data needed for the edicao (edit prescription) view.
        
        Args:
            request: Django HTTP request object
            
        Returns:
            ViewSetupResult: Contains all setup data or error information
        """
        try:
            self.logger.info(f"Setting up edit prescription view for user: {request.user}")
            
            # Step 1: Common setup (user, doctor, clinics)
            common_result = self._setup_common_data(request)
            if isinstance(common_result, SetupError):
                return common_result
            
            # Step 2: Validate edit prescription session requirements
            session_error = self._validate_edit_prescription_session(request, common_result.usuario)
            if session_error:
                return session_error
            
            # Step 3: Get edit-specific data
            cid = request.session["cid"]
            processo_id = int(request.session["processo_id"])
            processo = Processo.objects.get(id=processo_id, usuario=common_result.usuario)
            
            # Step 4: Get medications and form for edit
            med_repo = MedicationRepository()
            medicamentos = med_repo.list_medications_by_cid(cid)
            ModeloFormulario = fabricar_formulario(cid, True)  # True = edit/renewal form
            
            # Step 5: Get first date and prepare initial data from existing process
            try:
                primeira_data = request.session.get("data1", date.today().strftime("%d/%m/%Y"))
            except KeyError:
                primeira_data = date.today().strftime("%d/%m/%Y")
                self.logger.info(f"Using default primeira_data: {primeira_data}")
            
            # Create initial data from existing process with user's versioned data
            renewal_service = RenewalService()
            dados_iniciais = renewal_service.create_renewal_dictionary(processo, user=common_result.usuario)
            dados_iniciais["data_1"] = primeira_data
            dados_iniciais["clinicas"] = dados_iniciais["clinica"].id
            dados_iniciais = renewal_service._retrieve_prescription_data(dados_iniciais, processo)
            
            self.logger.info(f"Successfully set up edit prescription view for process: {processo_id}")
            
            return ViewSetupSuccess(
                common=common_result,
                form=PrescriptionFormData(
                    cid=cid,
                    medicamentos=medicamentos,
                    ModeloFormulario=ModeloFormulario
                ),
                specific=EditPrescriptionData(
                    processo_id=processo_id,
                    processo=processo,
                    dados_iniciais=dados_iniciais
                )
            )
            
        except Exception as e:
            self.logger.error(f"Error setting up edit prescription view: {e}", exc_info=True)
            return SetupError(
                message=f"Erro na inicialização: {e}",
                redirect_to="processos-busca"
            )
    
    def _setup_common_data(self, request) -> Union[SetupError, CommonSetupData]:
        """Set up data common to both cadastro and edicao views."""
        try:
            print(f"DEBUG COMMON: Starting common setup for user: {request.user}")
            # Get user and doctor
            usuario = request.user
            medico = seletor_medico(usuario)
            print(f"DEBUG COMMON: Got medico: {medico}")
            
            # Check if medico exists
            if not medico:
                print(f"DEBUG COMMON: No medico found, redirecting to home")
                self.logger.error(f"No doctor profile found for user: {usuario}")
                return SetupError(
                    message="Erro: perfil médico não encontrado. Contate o suporte.",
                    redirect_to="home"
                )
            
            # Get clinics and create choices
            clinicas = medico.clinicas.all()
            escolhas = self._create_clinic_choices(clinicas, usuario)
            
            self.logger.debug(f"Common setup complete - User: {usuario}, Clinics: {clinicas.count()}")
            
            return CommonSetupData(
                usuario=usuario,
                medico=medico,
                clinicas=clinicas,
                escolhas=escolhas
            )
            
        except Exception as e:
            self.logger.error(f"Error in common setup: {e}", exc_info=True)
            return SetupError(
                message=f"Erro ao carregar dados básicos: {e}",
                redirect_to="home"
            )
    
    def _create_clinic_choices(self, clinicas: QuerySet, usuario) -> Tuple:
        """Create clinic choices tuple with versioned names."""
        escolhas = []
        for c in clinicas:
            version = c.get_version_for_user(usuario)
            clinic_name = version.nome_clinica if version else c.nome_clinica
            escolhas.append((c.id, clinic_name))
        return tuple(escolhas)
    
    def _validate_new_prescription_session(self, request) -> Optional[SetupError]:
        """Validate session state for new prescription."""
        # Check for required session variables
        if "paciente_existe" not in request.session:
            self.logger.error("Missing paciente_existe in session")
            return SetupError(
                message="Sessão expirada. Por favor, inicie o cadastro novamente.",
                redirect_to="home"
            )
        
        if "cid" not in request.session:
            self.logger.error("Missing cid in session")
            return SetupError(
                message="CID não encontrado na sessão. Por favor, selecione o diagnóstico novamente.",
                redirect_to="home"
            )
        
        return None  # Success - no error
    
    def _validate_edit_prescription_session(self, request, usuario) -> Optional[SetupError]:
        """Validate session state for edit prescription."""
        # Check for required session variables
        if "cid" not in request.session:
            self.logger.error("Missing cid in session for edit")
            return SetupError(
                message="Erro na inicialização: CID não encontrado na sessão.",
                redirect_to="processos-busca"
            )
        
        if "processo_id" not in request.session:
            self.logger.error("Missing processo_id in session for edit")
            return SetupError(
                message="Processo não encontrado ou você não tem permissão para acessá-lo.",
                redirect_to="processos-busca"
            )
        
        # Verify user owns this process
        try:
            processo_id = int(request.session["processo_id"])
            processo = Processo.objects.get(id=processo_id, usuario=usuario)
            self.logger.debug(f"Process {processo_id} found and owned by user")
            return None  # Success - no error
            
        except (KeyError, ValueError, Processo.DoesNotExist) as e:
            self.logger.error(f"Error validating process ownership: {e}")
            return SetupError(
                message="Processo não encontrado ou você não tem permissão para acessá-lo.",
                redirect_to="processos-busca"
            )