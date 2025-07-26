"""
Domain Repository - Domain Entity Access Layer

This repository handles domain entity lookups for diseases and emitters.
It provides a clean interface for domain-related database operations.
"""

import logging
from typing import Optional

from processos.models import Doenca
from clinicas.models import Emissor


class DomainRepository:
    """
    Repository for domain entity access operations.
    
    This repository encapsulates domain entity lookups including:
    - Disease (Doenca) lookups by CID
    - Emissor lookups by medico and clinica
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_disease_by_cid(self, cid: str) -> Optional[Doenca]:
        """
        Get disease by CID code.
        
        Args:
            cid: The disease CID code
            
        Returns:
            Doenca: The disease instance if found
            
        Raises:
            Doenca.DoesNotExist: If disease not found
        """
        self.logger.debug(f"DomainRepository: Getting disease for CID {cid}")
        
        try:
            disease = Doenca.objects.get(cid=cid)
            self.logger.debug(f"DomainRepository: Found disease: {disease.nome}")
            return disease
        except Doenca.DoesNotExist:
            self.logger.error(f"DomainRepository: Disease not found for CID: {cid}")
            raise
    
    def get_emissor_by_medico_clinica(self, medico, clinica) -> Optional[Emissor]:
        """
        Get emissor by medico and clinica combination.
        
        Args:
            medico: The medico instance
            clinica: The clinica instance
            
        Returns:
            Emissor: The emissor instance if found
            
        Raises:
            Emissor.DoesNotExist: If emissor not found
        """
        self.logger.debug(f"DomainRepository: Getting emissor for medico {medico.id}, clinica {clinica.id}")
        
        try:
            emissor = Emissor.objects.get(medico=medico, clinica=clinica)
            self.logger.debug(f"DomainRepository: Found emissor: {emissor.id}")
            return emissor
        except Emissor.DoesNotExist:
            self.logger.error(f"DomainRepository: Emissor not found for medico/clinica")
            raise
    
    def get_all_diseases(self):
        """
        Get all diseases for form choices.
        
        Returns:
            QuerySet: All disease instances
        """
        self.logger.debug("DomainRepository: Getting all diseases")
        return Doenca.objects.all()