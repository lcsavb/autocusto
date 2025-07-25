"""
Model Utils - Django Model Utilities

This module contains pure utility functions for Django model operations.
These functions are stateless and have no business logic or side effects.

Extracted from helpers.py to follow utility pattern principles.
"""

import logging
from typing import Any, Dict


logger = logging.getLogger(__name__)


def prepare_model(model_class, **kwargs):
    """
    Prepare a Django model instance from a dictionary of data.
    
    This is a pure utility function that creates a model instance with the provided data.
    It's a simple wrapper around Django's model instantiation that makes the code more
    explicit and easier to test.
    
    Args:
        model_class: The Django model class (e.g., Paciente, Processo)
        **kwargs: Dictionary where keys are model field names and values are field data
        
    Returns:
        Model instance ready to be saved to the database
        
    Example:
        >>> patient = prepare_model(Paciente, nome_paciente="João", cpf_paciente="12345678901")
        >>> patient.save()
    """
    logger.debug(f"ModelUtils: Preparing {model_class.__name__} with {len(kwargs)} fields")
    
    # Create model instance with provided data
    model_instance = model_class(**kwargs)
    
    logger.debug(f"ModelUtils: Successfully prepared {model_class.__name__} instance")
    return model_instance


def model_to_dict_filtered(model_instance, fields: list = None, exclude: list = None) -> Dict[str, Any]:
    """
    Convert a Django model instance to dictionary with field filtering.
    
    This utility provides a clean interface for converting model instances to dictionaries
    with optional field filtering, which is useful for API serialization and data extraction.
    
    Args:
        model_instance: Django model instance to convert
        fields: List of fields to include (if provided, only these fields are included)
        exclude: List of fields to exclude (ignored if fields is provided)
        
    Returns:
        dict: Dictionary representation of the model instance
    """
    from django.forms.models import model_to_dict
    
    logger.debug(f"ModelUtils: Converting {model_instance.__class__.__name__} to dict")
    
    if fields:
        result = model_to_dict(model_instance, fields=fields)
        logger.debug(f"ModelUtils: Converted with {len(fields)} specific fields")
    elif exclude:
        result = model_to_dict(model_instance, exclude=exclude)
        logger.debug(f"ModelUtils: Converted excluding {len(exclude)} fields")
    else:
        result = model_to_dict(model_instance)
        logger.debug("ModelUtils: Converted all fields")
    
    return result


def extract_foreign_key_data(model_instance, fk_field_name: str) -> Dict[str, Any]:
    """
    Extract foreign key data as dictionary from a model instance.
    
    This utility safely extracts foreign key related data, handling None values
    and providing a clean interface for accessing related model data.
    
    Args:
        model_instance: Django model instance containing the foreign key
        fk_field_name: Name of the foreign key field
        
    Returns:
        dict: Dictionary representation of the foreign key model, empty if None
    """
    logger.debug(f"ModelUtils: Extracting FK data for {fk_field_name}")
    
    try:
        fk_instance = getattr(model_instance, fk_field_name)
        if fk_instance:
            result = model_to_dict(fk_instance)
            logger.debug(f"ModelUtils: Extracted {len(result)} fields from {fk_field_name}")
            return result
        else:
            logger.debug(f"ModelUtils: {fk_field_name} is None")
            return {}
    except AttributeError:
        logger.error(f"ModelUtils: Field {fk_field_name} not found on model")
        return {}


def bulk_prepare_models(model_class, data_list: list) -> list:
    """
    Prepare multiple model instances from a list of data dictionaries.
    
    This utility function is useful for bulk operations where you need to create
    multiple model instances at once.
    
    Args:
        model_class: The Django model class
        data_list: List of dictionaries, each containing data for one model instance
        
    Returns:
        list: List of prepared model instances ready for bulk operations
    """
    logger.debug(f"ModelUtils: Bulk preparing {len(data_list)} {model_class.__name__} instances")
    
    instances = []
    for index, data in enumerate(data_list):
        try:
            instance = model_class(**data)
            instances.append(instance)
        except Exception as e:
            logger.error(f"ModelUtils: Error preparing instance {index}: {e}")
            # Continue with other instances, don't fail the whole batch
    
    logger.debug(f"ModelUtils: Successfully prepared {len(instances)} instances")
    return instances