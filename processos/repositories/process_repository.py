"""
Process Repository - Process Data Access Layer

This repository handles process data access patterns, queries, and validation.
It provides a clean interface for process-related database operations.
"""

import logging
from typing import Optional
from django.core.exceptions import ObjectDoesNotExist

from processos.models import Processo


class ProcessRepository:
    """
    Repository for process data access and validation operations.
    
    This repository encapsulates all process-related database operations including:
    - Process existence checks with user authorization
    - Process data retrieval with access control
    - Process query operations
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_process_for_user(self, process_id: int, user) -> Optional[Processo]:
        """
        Get a process by ID ensuring the user has access to it.
        
        This method performs both process retrieval and authorization check,
        ensuring the user owns or has access to the process.
        
        Args:
            process_id: The process ID to retrieve
            user: The user requesting access
            
        Returns:
            Processo: The process instance if found and authorized
            None: If process doesn't exist or user lacks access
        """
        self.logger.debug(f"ProcessRepository: Getting process {process_id} for user {user.email}")
        
        try:
            processo = Processo.objects.get(id=process_id, usuario=user)
            self.logger.debug(f"ProcessRepository: Process {process_id} found and authorized")
            return processo
        except ObjectDoesNotExist:
            self.logger.warning(f"ProcessRepository: Process {process_id} not found or unauthorized for user {user.email}")
            return None
        except Exception as e:
            self.logger.error(f"ProcessRepository: Error retrieving process {process_id}: {e}")
            return None
    
    def get_process_with_disease_info(self, process_id: int, user) -> tuple[Optional[Processo], Optional[str]]:
        """
        Get a process and its disease CID ensuring user authorization.
        
        This method is commonly used when setting up sessions for process editing.
        
        Args:
            process_id: The process ID to retrieve
            user: The user requesting access
            
        Returns:
            tuple: (processo, cid) if found and authorized, (None, None) otherwise
        """
        self.logger.debug(f"ProcessRepository: Getting process {process_id} with disease info for user {user.email}")
        
        processo = self.get_process_for_user(process_id, user)
        if processo:
            cid = processo.doenca.cid
            self.logger.debug(f"ProcessRepository: Found process {process_id} with CID {cid}")
            return processo, cid
        
        self.logger.warning(f"ProcessRepository: No authorized process {process_id} found for user {user.email}")
        return None, None
    
    def get_process_by_id(self, process_id: int) -> Processo:
        """
        Get process by ID without user restriction - for internal operations.
        
        Args:
            process_id: The process ID to retrieve
            
        Returns:
            Processo: The process instance if found
            
        Raises:
            Processo.DoesNotExist: If process not found
        """
        self.logger.debug(f"ProcessRepository: Getting process {process_id} (no user check)")
        
        try:
            processo = Processo.objects.get(id=process_id)
            self.logger.debug(f"ProcessRepository: Found process {process_id}")
            return processo
        except Processo.DoesNotExist:
            self.logger.error(f"ProcessRepository: Process {process_id} not found")
            raise