# Import all forms and utilities from the new modular structure to maintain backward compatibility
from .forms.form_utilities import mostrar_med, ajustar_campos_condicionais
from .forms.validation_forms import PreProcesso, RenovacaoRapidaForm
from .forms.prescription_forms import NovoProcesso, RenovarProcesso
from .forms.form_factories import extrair_campos_condicionais, fabricar_formulario

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