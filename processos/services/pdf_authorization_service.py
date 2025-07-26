"""
PDF Authorization Service - Authorization and Security for PDF Access

This service handles the complex authorization logic for PDF file access,
including filename parsing, user authorization checks, and security validation.

Extracted from views to follow service-oriented architecture principles.
"""

import logging
from typing import Tuple, Optional
from django.http import Http404


class PDFAuthorizationService:
    """
    Service for PDF authorization and security operations.
    
    This service encapsulates:
    - PDF filename parsing and validation
    - User authorization checks for PDF access
    - Security validation (path traversal prevention)
    - CPF extraction and validation from filenames
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def authorize_pdf_access(self, user, filename: str) -> Tuple[bool, str]:
        """
        Authorize user access to a PDF file based on filename and user permissions.
        
        This method performs comprehensive authorization checking:
        1. Validates filename format and security
        2. Extracts patient CPF from filename
        3. Checks user access to patient records
        
        Args:
            user: The user requesting PDF access
            filename: The PDF filename to authorize
            
        Returns:
            Tuple of (is_authorized, cpf_paciente)
            
        Raises:
            Http404: If filename is invalid or access is denied
        """
        self.logger.info(f"Authorizing PDF access for user {user.email}, file: {filename}")
        
        # Step 1: Validate filename format and security
        self._validate_filename_security(filename)
        
        # Step 2: Parse and extract patient CPF
        cpf_paciente, cpf_raw = self._extract_cpf_from_filename(filename)
        
        # Step 3: Check user authorization
        has_access = self._check_user_patient_access(user, cpf_paciente, cpf_raw)
        
        if has_access:
            self.logger.info(f"User {user.email} authorized to access PDF for CPF {cpf_paciente}")
            return True, cpf_paciente
        else:
            self.logger.warning(f"User {user.email} attempted unauthorized access to PDF for CPF {cpf_paciente}")
            raise Http404("Access denied")
    
    def _validate_filename_security(self, filename: str) -> None:
        """
        Validate filename for security issues and format compliance.
        
        Args:
            filename: The filename to validate
            
        Raises:
            Http404: If filename fails security or format validation
        """
        # Basic file type validation
        if not filename.endswith('.pdf'):
            self.logger.warning(f"Invalid file type requested: {filename}")
            raise Http404("Invalid file type")
        
        # Directory traversal prevention
        if '..' in filename or '/' in filename or '\\' in filename:
            self.logger.warning(f"Directory traversal attempt: {filename}")
            raise Http404("Invalid filename")
        
        # PDF filename pattern validation
        if not filename.startswith('pdf_final_'):
            self.logger.warning(f"Invalid PDF filename pattern: {filename}")
            raise Http404("Invalid filename format")
        
        self.logger.debug(f"Filename security validation passed for: {filename}")
    
    def _extract_cpf_from_filename(self, filename: str) -> Tuple[str, str]:
        """
        Extract and validate CPF from PDF filename.
        
        Expected filename format: pdf_final_{cpf}_{cid}.pdf
        
        Args:
            filename: The PDF filename
            
        Returns:
            Tuple of (cleaned_cpf, raw_cpf)
            
        Raises:
            Http404: If CPF cannot be extracted or is invalid
        """
        try:
            # Remove prefix 'pdf_final_' and suffix '.pdf'
            core_name = filename[10:-4]
            parts = core_name.split('_')
            
            if len(parts) < 2:
                self.logger.warning(f"Invalid filename structure: {filename}")
                raise Http404("Invalid filename format")
            
            # First part is CPF, remaining parts form the CID
            cpf_raw = parts[0]
            
            # Clean CPF - remove dots and dashes to get only digits
            cpf_paciente = cpf_raw.replace('.', '').replace('-', '')
            
            # Verify CPF format (11 digits after cleaning)
            if not cpf_paciente.isdigit() or len(cpf_paciente) != 11:
                self.logger.warning(f"Invalid CPF format in filename: {cpf_raw} (cleaned: {cpf_paciente})")
                raise Http404("Invalid filename format")
            
            self.logger.debug(f"Successfully extracted CPF {cpf_paciente} from filename")
            return cpf_paciente, cpf_raw
            
        except (IndexError, ValueError) as e:
            self.logger.warning(f"Error parsing filename {filename}: {e}")
            raise Http404("Invalid filename format")
    
    def _check_user_patient_access(self, user, cpf_paciente: str, cpf_raw: str) -> bool:
        """
        Check if user has access to patient with given CPF.
        
        Args:
            user: The user to check access for
            cpf_paciente: Cleaned CPF (digits only)
            cpf_raw: Original CPF from filename (may include formatting)
            
        Returns:
            bool: True if user has access, False otherwise
        """
        try:
            # Check if current user has access to patient with this CPF
            # Try both cleaned CPF and original formatted CPF from filename
            has_access = (
                user.pacientes.filter(cpf_paciente=cpf_paciente).exists() or
                user.pacientes.filter(cpf_paciente=cpf_raw).exists()
            )
            
            self.logger.debug(f"User {user.email} access check for CPF {cpf_paciente}: {'GRANTED' if has_access else 'DENIED'}")
            return has_access
            
        except Exception as e:
            self.logger.error(f"Error during authorization check: {e}")
            return False  # Fail secure - deny access on error