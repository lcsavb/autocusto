"""
Data Utils - Data Transformation Utilities

This module contains pure utility functions for data transformation and formatting.
These functions are stateless and have no business logic or side effects.

Extracted from helpers.py to follow utility pattern principles.
"""

import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime


logger = logging.getLogger(__name__)


def link_issuer_data(usuario, medico, clinica, form_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Link issuer (user, doctor, clinic) data to form data dictionary.
    
    This utility function adds issuer information to the main form data dictionary.
    It's a pure data transformation function with no side effects.
    
    Args:
        usuario: User instance
        medico: Doctor instance  
        clinica: Clinic instance
        form_data: Form data dictionary to update
        
    Returns:
        dict: Updated form data dictionary with issuer information
    """
    from django.forms.models import model_to_dict
    
    logger.debug("DataUtils: Linking issuer data to form")
    
    # Extract doctor data
    medico_fields = ['nome_medico', 'cns_medico', 'crm_medico']
    medico_data = model_to_dict(medico, fields=medico_fields)
    
    # Extract clinic data
    clinica_fields = ['nome_clinica', 'cns_clinica', 'cidade', 'bairro', 'cep', 'telefone_clinica']
    clinica_data = model_to_dict(clinica, fields=clinica_fields)
    
    # Build clinic address
    clinic_address = f"{clinica.logradouro}, {clinica.logradouro_num}"
    clinica_data["end_clinica"] = clinic_address
    
    # Combine all issuer data
    issuer_data = {
        **medico_data,
        **clinica_data,
        "usuario": usuario,
    }
    
    # Update form data with issuer information
    form_data.update(issuer_data)
    
    logger.debug(f"DataUtils: Linked {len(issuer_data)} issuer fields to form data")
    return form_data


def format_date_for_pdftk(date_value) -> str:
    """
    Format date value for pdftk PDF generation.
    
    This utility ensures date values are properly formatted as strings
    for PDF form filling operations.
    
    Args:
        date_value: Date value (datetime, string, or None)
        
    Returns:
        str: Formatted date string suitable for pdftk
    """
    logger.debug(f"DataUtils: Formatting date {date_value} for pdftk")
    
    if not date_value:
        return ""
    
    if isinstance(date_value, datetime):
        formatted = date_value.strftime("%d/%m/%Y")
    elif isinstance(date_value, str):
        formatted = date_value
    else:
        formatted = str(date_value)
    
    logger.debug(f"DataUtils: Formatted date as {formatted}")
    return formatted


def sanitize_for_pdftk(data_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize dictionary data for pdftk PDF generation.
    
    This utility ensures all values are properly formatted as strings
    and handles None values that could cause pdftk to fail.
    
    Args:
        data_dict: Dictionary to sanitize
        
    Returns:
        dict: Sanitized dictionary with string values
    """
    logger.debug(f"DataUtils: Sanitizing {len(data_dict)} fields for pdftk")
    
    sanitized = {}
    
    for key, value in data_dict.items():
        if value is None:
            sanitized[key] = ""
        elif isinstance(value, bool):
            sanitized[key] = "Sim" if value else "Não"
        elif isinstance(value, datetime):
            sanitized[key] = value.strftime("%d/%m/%Y")
        elif isinstance(value, (list, tuple)):
            sanitized[key] = ", ".join(str(item) for item in value)
        else:
            sanitized[key] = str(value)
    
    logger.debug(f"DataUtils: Sanitized {len(sanitized)} fields")
    return sanitized


def merge_dictionaries(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple dictionaries into a single dictionary.
    
    This utility function safely merges dictionaries, with later dictionaries
    overriding values from earlier ones in case of key conflicts.
    
    Args:
        *dicts: Variable number of dictionaries to merge
        
    Returns:
        dict: Merged dictionary containing all key-value pairs
    """
    logger.debug(f"DataUtils: Merging {len(dicts)} dictionaries")
    
    merged = {}
    total_keys = 0
    
    for dict_item in dicts:
        if dict_item:
            merged.update(dict_item)
            total_keys += len(dict_item)
    
    logger.debug(f"DataUtils: Merged {total_keys} total keys into {len(merged)} unique keys")
    return merged


def extract_conditional_fields(form_data: Dict[str, Any], prefix: str = "opt_") -> Dict[str, Any]:
    """
    Extract fields with a specific prefix from form data.
    
    This utility is commonly used to extract conditional fields that are
    protocol-specific or optional in nature.
    
    Args:
        form_data: Dictionary to extract from
        prefix: Prefix to filter by (default: "opt_")
        
    Returns:
        dict: Dictionary containing only fields with the specified prefix
    """
    logger.debug(f"DataUtils: Extracting fields with prefix '{prefix}'")
    
    conditional_fields = {}
    
    for key, value in form_data.items():
        if key.startswith(prefix):
            conditional_fields[key] = value
    
    logger.debug(f"DataUtils: Extracted {len(conditional_fields)} conditional fields")
    return conditional_fields


def clean_empty_values(data_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove keys with empty or None values from dictionary.
    
    This utility cleans up dictionaries by removing entries that have
    no meaningful data, which is useful for API responses and data processing.
    
    Args:
        data_dict: Dictionary to clean
        
    Returns:
        dict: Cleaned dictionary with empty values removed
    """
    logger.debug(f"DataUtils: Cleaning empty values from {len(data_dict)} fields")
    
    cleaned = {}
    
    for key, value in data_dict.items():
        if value is not None and value != "" and value != []:
            cleaned[key] = value
    
    removed_count = len(data_dict) - len(cleaned)
    logger.debug(f"DataUtils: Removed {removed_count} empty fields, {len(cleaned)} remaining")
    
    return cleaned


def validate_required_fields(data_dict: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """
    Validate that required fields are present and not empty in dictionary.
    
    This utility function checks for the presence of required fields and
    returns a list of missing or empty fields.
    
    Args:
        data_dict: Dictionary to validate
        required_fields: List of field names that are required
        
    Returns:
        list: List of missing or empty field names
    """
    logger.debug(f"DataUtils: Validating {len(required_fields)} required fields")
    
    missing_fields = []
    
    for field in required_fields:
        if field not in data_dict or not data_dict[field]:
            missing_fields.append(field)
    
    logger.debug(f"DataUtils: Found {len(missing_fields)} missing required fields")
    return missing_fields