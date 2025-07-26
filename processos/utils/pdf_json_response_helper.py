"""
PDF JSON Response Helper - View Layer Utility

This helper eliminates duplicated JSON response creation logic for AJAX PDF operations
across multiple views (cadastro, edicao, renovacao_rapida).

Note: This is different from PDFResponseBuilder which creates HttpResponse for serving PDFs.
This creates JsonResponse for AJAX requests about PDF generation status.
"""

import logging
from typing import Dict, Any, Optional
from django.http import JsonResponse


logger = logging.getLogger(__name__)


class PDFJsonResponseHelper:
    """
    Helper class to create consistent JSON responses for AJAX PDF operations.
    
    This eliminates duplication across views while maintaining consistent
    error handling and response formatting for AJAX requests.
    
    NOT to be confused with PDFResponseBuilder which creates HttpResponse
    for serving actual PDF files.
    """
    
    # Standard messages for different operations
    MESSAGES = {
        'create': 'Processo criado com sucesso! PDF gerado.',
        'update': 'Processo atualizado com sucesso! PDF gerado.',
        'renew': 'Renovação processada com sucesso! PDF gerado.'
    }
    
    # Standard error messages
    ERRORS = {
        'pdf_generation_failed': 'Falha ao gerar PDF. Verifique se todos os arquivos necessários estão disponíveis.',
        'pdf_save_failed': 'Falha ao salvar PDF. Verifique se todos os arquivos necessários estão disponíveis.',
        'form_validation_failed': 'Erro de validação do formulário.',
        'duplicate_process': 'Este processo já existe para este paciente. Verifique se não há duplicatas.',
        'process_not_found': 'Processo não encontrado.',
        'internal_error': 'Erro interno no servidor.'
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def success(
        self, 
        pdf_url: str, 
        processo_id: int, 
        operation: str = 'create',
        filename: Optional[str] = None,
        **kwargs
    ) -> JsonResponse:
        """
        Create a successful JSON response for PDF generation.
        
        Args:
            pdf_url: URL where the PDF can be accessed
            processo_id: ID of the process
            operation: Type of operation ('create', 'update', 'renew')
            filename: Name of the PDF file
            **kwargs: Any additional data to include in response
            
        Returns:
            JsonResponse with success data
        """
        response_data = {
            'success': True,
            'pdf_url': pdf_url,
            'processo_id': processo_id,
            'message': self.MESSAGES.get(operation, self.MESSAGES['create'])
        }
        
        if filename:
            response_data['filename'] = filename
            
        # Add any additional data
        response_data.update(kwargs)
        
        self.logger.info(f"PDF JSON response success: Process {processo_id}, Operation: {operation}")
        return JsonResponse(response_data)
    
    def error(
        self,
        error_type: str = 'internal_error',
        custom_message: Optional[str] = None,
        form_errors: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> JsonResponse:
        """
        Create an error JSON response.
        
        Args:
            error_type: Type of error from ERRORS dict
            custom_message: Custom error message (overrides error_type)
            form_errors: Form validation errors if any
            **kwargs: Any additional data to include in response
            
        Returns:
            JsonResponse with error data
        """
        response_data = {
            'success': False,
            'error': custom_message or self.ERRORS.get(error_type, self.ERRORS['internal_error'])
        }
        
        if form_errors:
            response_data['form_errors'] = form_errors
            
        # Add any additional data
        response_data.update(kwargs)
        
        self.logger.error(f"PDF JSON response error: {response_data['error']}")
        return JsonResponse(response_data)
    
    def pdf_generation_failed(self) -> JsonResponse:
        """Standard response for PDF generation failure."""
        return self.error('pdf_generation_failed')
    
    def pdf_save_failed(self) -> JsonResponse:
        """Standard response for PDF save failure."""
        return self.error('pdf_save_failed')
    
    def form_validation_failed(self, form_errors: Dict[str, Any]) -> JsonResponse:
        """Standard response for form validation failure."""
        return self.error('form_validation_failed', form_errors=form_errors)
    
    def duplicate_process(self) -> JsonResponse:
        """Standard response for duplicate process error."""
        return self.error('duplicate_process')
    
    def exception(self, exception: Exception, context: str = "processamento") -> JsonResponse:
        """
        Create response for unexpected exceptions.
        
        Args:
            exception: The exception that occurred
            context: Context where the error occurred
            
        Returns:
            JsonResponse with exception details
        """
        error_message = f'Erro no {context}: {str(exception)}'
        self.logger.error(f"Exception in PDF operation: {error_message}", exc_info=True)
        return self.error(custom_message=error_message)