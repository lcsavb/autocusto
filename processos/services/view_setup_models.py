"""
View Setup Data Models

Focused data classes for prescription view setup, replacing the monolithic SetupResult.
These classes follow the Single Responsibility Principle and use composition for clarity.
"""

from dataclasses import dataclass
from typing import Optional, Any, List, Tuple, Union
from django.db.models import QuerySet
from processos.models import Processo


@dataclass
class SetupError:
    """Represents an error during view setup."""
    message: str
    redirect_to: str


@dataclass
class CommonSetupData:
    """Data common to all prescription views (cadastro and edicao)."""
    usuario: Any  # User object
    medico: Any   # Medico object
    clinicas: QuerySet  # Available clinics for the user
    escolhas: Tuple  # Clinic choices for form


@dataclass
class PrescriptionFormData:
    """Form-related data for prescription views."""
    cid: str  # Disease CID code
    medicamentos: List  # Available medications
    ModeloFormulario: type  # Form class to use


@dataclass
class NewPrescriptionData:
    """Data specific to new prescription creation (cadastro view)."""
    paciente_existe: bool  # Whether patient already exists
    primeira_data: Optional[str]  # Initial prescription date
    dados_iniciais: dict  # Initial form data for new prescription


@dataclass
class EditPrescriptionData:
    """Data specific to prescription editing (edicao view)."""
    processo_id: int  # Process being edited
    processo: Processo  # Process object
    dados_iniciais: dict  # Initial form data from existing process


@dataclass
class ViewSetupSuccess:
    """Successful view setup result with all required data."""
    common: CommonSetupData
    form: PrescriptionFormData
    specific: Union[NewPrescriptionData, EditPrescriptionData]


# Union type for setup results
ViewSetupResult = Union[SetupError, ViewSetupSuccess]


def is_setup_error(result: ViewSetupResult) -> bool:
    """Type guard to check if setup result is an error."""
    return isinstance(result, SetupError)


def is_setup_success(result: ViewSetupResult) -> bool:
    """Type guard to check if setup result is successful."""
    return isinstance(result, ViewSetupSuccess)