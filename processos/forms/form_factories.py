"""
Form Factories - Dynamic form generation and field extraction

This module contains functions for dynamic form creation and field manipulation:
- fabricar_formulario: Creates dynamic forms based on disease protocols
- extrair_campos_condicionais: Extracts conditional fields from forms
"""

import logging
from processos.models import Protocolo
from processos.services.pdf_strategies import get_conditional_fields

logger = logging.getLogger('processos')


def extrair_campos_condicionais(formulario):
    """
    Extract conditional fields from a form based on field name patterns.
    
    This function identifies fields that are conditionally displayed
    based on the 'opt_' prefix naming convention.
    
    Args:
        formulario: Django form instance
        
    Returns:
        list: List of conditional form fields
    """
    campos_condicionais = []
    for campo in formulario:
        if campo.name[0:4] == "opt_":
            campos_condicionais.append(campo)
    return campos_condicionais


def fabricar_formulario(cid, renovar):
    """
    Dynamically create form classes based on disease protocol and operation type.
    
    This factory function creates specialized form classes by combining base forms
    with protocol-specific conditional fields. It supports both new prescriptions
    and renewal operations.
    
    Args:
        cid (str): Disease CID code to determine protocol
        renovar (bool): True for renewal forms, False for new prescription forms
        
    Returns:
        type: Dynamically created form class with protocol-specific fields
    """
    from .prescription_forms import RenovarProcesso, NovoProcesso
    
    # Select base form based on operation type
    if renovar:
        modelo_base = RenovarProcesso
    else:
        modelo_base = NovoProcesso

    # Get protocol for the disease
    try:
        protocolo = Protocolo.objects.get(doenca__cid=cid)
    except Protocolo.DoesNotExist:
        logger.warning(f"No protocol found for CID {cid}")
        # Return base form without conditional fields
        return modelo_base

    # Try new data-driven approach first, fallback to empty fields for unmigrated protocols
    campos = get_conditional_fields(protocolo)
    if not campos:
        # Legacy protocols without data-driven configuration will have no conditional fields
        # This maintains backward compatibility until all protocols are migrated
        campos = {}
        logger.debug(f"No conditional fields configured for {protocolo.nome} - protocol needs migration")
    else:
        logger.debug(f"Using data-driven conditional fields for {protocolo.nome}")

    # Create dynamic form class with protocol-specific fields
    # This uses Python's type() function to create a new class at runtime
    # The resulting class inherits from the base form and adds conditional fields
    return type("SuperForm", (modelo_base,), campos)