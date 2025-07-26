# Import all views to maintain backward compatibility
from .pdf_views import pdf, serve_pdf
from .session_views import set_edit_session
from .prescription_views import edicao, cadastro
from .search_views import busca_processos
from .renewal_views import renovacao_rapida

# Maintain backward compatibility by exposing all views at package level
__all__ = [
    'pdf',
    'serve_pdf', 
    'set_edit_session',
    'edicao',
    'cadastro',
    'busca_processos',
    'renovacao_rapida'
]