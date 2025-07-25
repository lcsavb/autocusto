from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def patient_name_for_user(patient, user):
    """
    Template filter to show patient name as seen by the user (versioned).
    
    Usage in template:
    {{ paciente|patient_name_for_user:user }}
    
    Security: Only returns data if user has version access - no fallback to master record.
    """
    if not patient or not user:
        return ""
    
    try:
        version = patient.get_version_for_user(user)
        if version:
            return version.nome_paciente
        else:
            # Security: No fallback - return empty string if no version access
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"Security: Template access denied to patient CPF {patient.cpf_paciente} "
                f"for user {user.email} - no version access"
            )
            return "[Acesso Negado]"
    except Exception as e:
        # Security: No fallback - log error and return access denied
        import logging
        logger = logging.getLogger(__name__)
        logger.error(
            f"Security: Template filter error for patient {getattr(patient, 'cpf_paciente', 'unknown')} "
            f"and user {getattr(user, 'email', 'unknown')}: {e}"
        )
        return "[Erro de Acesso]"


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
    
    Security: Only returns data if user has version access - no fallback to master record.
    """
    if not patient or not user:
        return None
    
    try:
        version = patient.get_version_for_user(user)
        if version:
            return version
        else:
            # Security: No fallback - return None if no version access
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"Security: Template data access denied to patient CPF {patient.cpf_paciente} "
                f"for user {user.email} - no version access"
            )
            return None
    except Exception as e:
        # Security: No fallback - log error and return None
        import logging
        logger = logging.getLogger(__name__)
        logger.error(
            f"Security: Template data filter error for patient {getattr(patient, 'cpf_paciente', 'unknown')} "
            f"and user {getattr(user, 'email', 'unknown')}: {e}"
        )
        return None