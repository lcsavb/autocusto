# Import all views from the new modular structure to maintain backward compatibility
from .views.pdf_views import pdf, serve_pdf
from .views.session_views import set_edit_session
from .views.prescription_views import edicao, cadastro
from .views.search_views import busca_processos
from .views.renewal_views import renovacao_rapida

# Re-export for URL routing
__all__ = [
    'pdf',
    'serve_pdf', 
    'set_edit_session',
    'edicao',
    'cadastro',
    'busca_processos',
    'renovacao_rapida'
]