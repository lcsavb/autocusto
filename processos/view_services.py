"""
View Services - Setup and Data Preparation for Views

This module provides services that handle the complex setup logic for prescription views.
These services extract the heavy lifting from views, making them thin controllers that
focus only on HTTP concerns.

Services:
- PrescriptionViewSetupService: Handles all setup logic for prescription views
"""

import logging
from typing import NamedTuple, Optional, List, Tuple, Any
from datetime import date

from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import QuerySet

from medicos.seletor import medico as seletor_medico
from processos.models import Processo, Doenca
from processos.helpers import listar_med, cria_dict_renovação, resgatar_prescricao
from processos.forms import fabricar_formulario
from processos.views import _get_initial_data


logger = logging.getLogger(__name__)


class SetupResult(NamedTuple):
    """Result object containing all setup data for prescription views."""
    success: bool
    error_redirect: Optional[str]
    error_message: Optional[str]
    
    # Common setup data
    usuario: Optional[Any]
    medico: Optional[Any]
    clinicas: Optional[QuerySet]
    escolhas: Optional[Tuple]
    cid: Optional[str]
    medicamentos: Optional[List]
    ModeloFormulario: Optional[type]
    
    # Edit-specific data
    processo_id: Optional[int]
    processo: Optional[Processo]
    dados_iniciais: Optional[dict]
    
    # New prescription-specific data
    paciente_existe: Optional[bool]
    primeira_data: Optional[str]


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
    
    def setup_for_new_prescription(self, request) -> SetupResult:
        """
        Set up all data needed for the cadastro (new prescription) view.
        
        Args:
            request: Django HTTP request object
            
        Returns:
            SetupResult: Contains all setup data or error information
        """
        try:
            self.logger.info(f"Setting up new prescription view for user: {request.user}")
            
            # Step 1: Common setup (user, doctor, clinics)
            common_result = self._setup_common_data(request)
            if not common_result.success:
                return common_result
            
            # Step 2: Validate new prescription session requirements
            session_result = self._validate_new_prescription_session(request)
            if not session_result.success:
                return session_result
            
            # Step 3: Get prescription-specific data
            paciente_existe = request.session["paciente_existe"]
            primeira_data = date.today().strftime("%d/%m/%Y")
            cid = request.session["cid"]
            
            # Step 4: Get medications and form for new prescription
            medicamentos = listar_med(cid)
            ModeloFormulario = fabricar_formulario(cid, False)  # False = new prescription
            
            # Step 5: Prepare initial data based on patient existence
            try:
                dados_iniciais = _get_initial_data(request, paciente_existe, primeira_data, cid)
            except KeyError as e:
                self.logger.error(f"Missing session data for initial data: {e}")
                return SetupResult(
                    success=False,
                    error_redirect="home",
                    error_message=str(e),
                    usuario=None, medico=None, clinicas=None, escolhas=None,
                    cid=None, medicamentos=None, ModeloFormulario=None,
                    processo_id=None, processo=None, dados_iniciais=None,
                    paciente_existe=None, primeira_data=None
                )
            
            self.logger.info(f"Successfully set up new prescription view for CID: {cid}")
            
            return SetupResult(
                success=True,
                error_redirect=None,
                error_message=None,
                usuario=common_result.usuario,
                medico=common_result.medico,
                clinicas=common_result.clinicas,
                escolhas=common_result.escolhas,
                cid=cid,
                medicamentos=medicamentos,
                ModeloFormulario=ModeloFormulario,
                processo_id=None,
                processo=None,
                dados_iniciais=dados_iniciais,
                paciente_existe=paciente_existe,
                primeira_data=primeira_data
            )
            
        except Exception as e:
            self.logger.error(f"Error setting up new prescription view: {e}", exc_info=True)
            return SetupResult(
                success=False,
                error_redirect="home",
                error_message=f"Erro ao carregar dados do cadastro: {e}",
                usuario=None, medico=None, clinicas=None, escolhas=None,
                cid=None, medicamentos=None, ModeloFormulario=None,
                processo_id=None, processo=None, dados_iniciais=None,
                paciente_existe=None, primeira_data=None
            )
    
    def setup_for_edit_prescription(self, request) -> SetupResult:
        """
        Set up all data needed for the edicao (edit prescription) view.
        
        Args:
            request: Django HTTP request object
            
        Returns:
            SetupResult: Contains all setup data or error information
        """
        try:
            self.logger.info(f"Setting up edit prescription view for user: {request.user}")
            
            # Step 1: Common setup (user, doctor, clinics)
            common_result = self._setup_common_data(request)
            if not common_result.success:
                return common_result
            
            # Step 2: Validate edit prescription session requirements
            session_result = self._validate_edit_prescription_session(request, common_result.usuario)
            if not session_result.success:
                return session_result
            
            # Step 3: Get edit-specific data
            cid = request.session["cid"]
            processo_id = session_result.processo_id
            processo = session_result.processo
            
            # Step 4: Get medications and form for edit
            medicamentos = listar_med(cid)
            ModeloFormulario = fabricar_formulario(cid, True)  # True = edit/renewal form
            
            # Step 5: Get first date and prepare initial data from existing process
            try:
                primeira_data = request.session.get("data1", date.today().strftime("%d/%m/%Y"))
            except KeyError:
                primeira_data = date.today().strftime("%d/%m/%Y")
                self.logger.info(f"Using default primeira_data: {primeira_data}")
            
            # Create initial data from existing process with user's versioned data
            dados_iniciais = cria_dict_renovação(processo, user=common_result.usuario)
            dados_iniciais["data_1"] = primeira_data
            dados_iniciais["clinicas"] = dados_iniciais["clinica"].id
            dados_iniciais = resgatar_prescricao(dados_iniciais, processo)
            
            self.logger.info(f"Successfully set up edit prescription view for process: {processo_id}")
            
            return SetupResult(
                success=True,
                error_redirect=None,
                error_message=None,
                usuario=common_result.usuario,
                medico=common_result.medico,
                clinicas=common_result.clinicas,
                escolhas=common_result.escolhas,
                cid=cid,
                medicamentos=medicamentos,
                ModeloFormulario=ModeloFormulario,
                processo_id=processo_id,
                processo=processo,
                dados_iniciais=dados_iniciais,
                paciente_existe=True,  # For edit, patient always exists
                primeira_data=primeira_data
            )
            
        except Exception as e:
            self.logger.error(f"Error setting up edit prescription view: {e}", exc_info=True)
            return SetupResult(
                success=False,
                error_redirect="processos-busca",
                error_message=f"Erro na inicialização: {e}",
                usuario=None, medico=None, clinicas=None, escolhas=None,
                cid=None, medicamentos=None, ModeloFormulario=None,
                processo_id=None, processo=None, dados_iniciais=None,
                paciente_existe=None, primeira_data=None
            )
    
    def _setup_common_data(self, request) -> SetupResult:
        """Set up data common to both cadastro and edicao views."""
        try:
            # Get user and doctor
            usuario = request.user
            medico = seletor_medico(usuario)
            
            # Check if medico exists
            if not medico:
                self.logger.error(f"No doctor profile found for user: {usuario}")
                return SetupResult(
                    success=False,
                    error_redirect="home",
                    error_message="Erro: perfil médico não encontrado. Contate o suporte.",
                    usuario=usuario, medico=None, clinicas=None, escolhas=None,
                    cid=None, medicamentos=None, ModeloFormulario=None,
                    processo_id=None, processo=None, dados_iniciais=None,
                    paciente_existe=None, primeira_data=None
                )
            
            # Get clinics and create choices
            clinicas = medico.clinicas.all()
            escolhas = self._create_clinic_choices(clinicas, usuario)
            
            self.logger.debug(f"Common setup complete - User: {usuario}, Clinics: {clinicas.count()}")
            
            return SetupResult(
                success=True,
                error_redirect=None,
                error_message=None,
                usuario=usuario,
                medico=medico,
                clinicas=clinicas,
                escolhas=escolhas,
                cid=None, medicamentos=None, ModeloFormulario=None,
                processo_id=None, processo=None, dados_iniciais=None,
                paciente_existe=None, primeira_data=None
            )
            
        except Exception as e:
            self.logger.error(f"Error in common setup: {e}", exc_info=True)
            return SetupResult(
                success=False,
                error_redirect="home",
                error_message=f"Erro ao carregar dados básicos: {e}",
                usuario=None, medico=None, clinicas=None, escolhas=None,
                cid=None, medicamentos=None, ModeloFormulario=None,
                processo_id=None, processo=None, dados_iniciais=None,
                paciente_existe=None, primeira_data=None
            )
    
    def _create_clinic_choices(self, clinicas: QuerySet, usuario) -> Tuple:
        """Create clinic choices tuple with versioned names."""
        escolhas = []
        for c in clinicas:
            version = c.get_version_for_user(usuario)
            clinic_name = version.nome_clinica if version else c.nome_clinica
            escolhas.append((c.id, clinic_name))
        return tuple(escolhas)
    
    def _validate_new_prescription_session(self, request) -> SetupResult:
        """Validate session state for new prescription."""
        # Check for required session variables
        if "paciente_existe" not in request.session:
            self.logger.error("Missing paciente_existe in session")
            return SetupResult(
                success=False,
                error_redirect="home",
                error_message="Sessão expirada. Por favor, inicie o cadastro novamente.",
                usuario=None, medico=None, clinicas=None, escolhas=None,
                cid=None, medicamentos=None, ModeloFormulario=None,
                processo_id=None, processo=None, dados_iniciais=None,
                paciente_existe=None, primeira_data=None
            )
        
        if "cid" not in request.session:
            self.logger.error("Missing cid in session")
            return SetupResult(
                success=False,
                error_redirect="home",
                error_message="CID não encontrado na sessão. Por favor, selecione o diagnóstico novamente.",
                usuario=None, medico=None, clinicas=None, escolhas=None,
                cid=None, medicamentos=None, ModeloFormulario=None,
                processo_id=None, processo=None, dados_iniciais=None,
                paciente_existe=None, primeira_data=None
            )
        
        return SetupResult(
            success=True,
            error_redirect=None, error_message=None,
            usuario=None, medico=None, clinicas=None, escolhas=None,
            cid=None, medicamentos=None, ModeloFormulario=None,
            processo_id=None, processo=None, dados_iniciais=None,
            paciente_existe=None, primeira_data=None
        )
    
    def _validate_edit_prescription_session(self, request, usuario) -> SetupResult:
        """Validate session state for edit prescription."""
        # Check for required session variables
        if "cid" not in request.session:
            self.logger.error("Missing cid in session for edit")
            return SetupResult(
                success=False,
                error_redirect="processos-busca",
                error_message="Erro na inicialização: CID não encontrado na sessão.",
                usuario=None, medico=None, clinicas=None, escolhas=None,
                cid=None, medicamentos=None, ModeloFormulario=None,
                processo_id=None, processo=None, dados_iniciais=None,
                paciente_existe=None, primeira_data=None
            )
        
        if "processo_id" not in request.session:
            self.logger.error("Missing processo_id in session for edit")
            return SetupResult(
                success=False,
                error_redirect="processos-busca",
                error_message="Processo não encontrado ou você não tem permissão para acessá-lo.",
                usuario=None, medico=None, clinicas=None, escolhas=None,
                cid=None, medicamentos=None, ModeloFormulario=None,
                processo_id=None, processo=None, dados_iniciais=None,
                paciente_existe=None, primeira_data=None
            )
        
        # Verify user owns this process
        try:
            processo_id = int(request.session["processo_id"])
            processo = Processo.objects.get(id=processo_id, usuario=usuario)
            self.logger.debug(f"Process {processo_id} found and owned by user")
            
            return SetupResult(
                success=True,
                error_redirect=None, error_message=None,
                usuario=None, medico=None, clinicas=None, escolhas=None,
                cid=None, medicamentos=None, ModeloFormulario=None,
                processo_id=processo_id, processo=processo, dados_iniciais=None,
                paciente_existe=None, primeira_data=None
            )
            
        except (KeyError, ValueError, Processo.DoesNotExist) as e:
            self.logger.error(f"Error validating process ownership: {e}")
            return SetupResult(
                success=False,
                error_redirect="processos-busca",
                error_message="Processo não encontrado ou você não tem permissão para acessá-lo.",
                usuario=None, medico=None, clinicas=None, escolhas=None,
                cid=None, medicamentos=None, ModeloFormulario=None,
                processo_id=None, processo=None, dados_iniciais=None,
                paciente_existe=None, primeira_data=None
            )