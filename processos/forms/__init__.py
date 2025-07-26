# Import all forms and utilities to maintain backward compatibility
from .form_utilities import mostrar_med, ajustar_campos_condicionais
from .validation_forms import PreProcesso, RenovacaoRapidaForm
from .prescription_forms import NovoProcesso, RenovarProcesso
from .form_factories import extrair_campos_condicionais, fabricar_formulario

# Re-export for backward compatibility
__all__ = [
    'mostrar_med',
    'ajustar_campos_condicionais', 
    'PreProcesso',
    'RenovacaoRapidaForm',
    'NovoProcesso',
    'RenovarProcesso',
    'extrair_campos_condicionais',
    'fabricar_formulario'
]