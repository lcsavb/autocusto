"""
Test Session Data Configuration - Centralized session data for tests
Simple dictionaries and lists for consistent test session setup.
"""

# Required session keys for different workflows
SESSION_KEYS = {
    'edicao': ['processo_id', 'cid'],
    'cadastro': ['cpf_paciente', 'cid', 'paciente_existe'], 
    'renovacao': ['processo_id', 'cid', 'data1'],
}

# Default session data templates
DEFAULT_SESSION_DATA = {
    'edicao': {
        'cid': 'G40.0',  # Default epilepsy CID
        # processo_id will be set dynamically
    },
    'cadastro': {
        'cid': 'G40.0',
        'paciente_existe': True,
        # cpf_paciente will be set dynamically
    },
    'renovacao': {
        'cid': 'G40.0', 
        'data1': '01/01/2024',
        # processo_id will be set dynamically
    }
}

# Common test diseases
TEST_DISEASES = {
    'epilepsy': 'G40.0',
    'diabetes': 'E10.9',
    'hypertension': 'I10',
}

# Session setup helper functions
def get_edicao_session_data(processo_id, cid='G40.0'):
    """Get session data for edicao workflow."""
    return {
        'processo_id': processo_id,
        'cid': cid,
    }

def get_cadastro_session_data(cpf_paciente, cid='G40.0', paciente_existe=True):
    """Get session data for cadastro workflow."""
    return {
        'cpf_paciente': cpf_paciente,
        'cid': cid,
        'paciente_existe': paciente_existe,
    }

def get_renovacao_session_data(processo_id, cid='G40.0', data1='01/01/2024'):
    """Get session data for renovacao workflow."""
    return {
        'processo_id': processo_id,
        'cid': cid,
        'data1': data1,
    }