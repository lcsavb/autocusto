from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def patient_name_for_user(patient, user):
    """
    Template filter to show patient name as seen by the user (versioned).
    
    Usage in template:
    {{ paciente|patient_name_for_user:user }}
    
    Returns the versioned patient name if available, otherwise the master record name.
    """
    if not patient or not user:
        return ""
    
    try:
        version = patient.get_version_for_user(user)
        return version.nome_paciente if version else patient.nome_paciente
    except:
        # Fallback to master record if anything goes wrong
        return patient.nome_paciente


@register.filter  
def patient_data_for_user(patient, user):
    """
    Template filter to get all patient data as seen by the user (versioned).
    
    Usage in template:
    {% with patient_data=paciente|patient_data_for_user:user %}
        {{ patient_data.nome_paciente }}
        {{ patient_data.idade }}
        etc.
    {% endwith %}
    
    Returns the versioned patient data if available, otherwise the master record.
    """
    if not patient or not user:
        return patient
    
    try:
        version = patient.get_version_for_user(user)
        return version if version else patient
    except:
        # Fallback to master record if anything goes wrong
        return patient