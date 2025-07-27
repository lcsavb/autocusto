"""
Doctor Repository - Doctor Data Access Layer

This repository handles doctor data access patterns, queries, and validation.
It provides a clean interface for doctor-related database operations.
"""

import logging
from typing import Dict, Any, Optional, Union, List
from django.db.models import QuerySet
from django.contrib.auth import get_user_model

from medicos.models import Medico

User = get_user_model()
logger = logging.getLogger('medicos.repository')


class DoctorRepository:
    """
    Repository for doctor data access and validation operations.
    
    This repository encapsulates all doctor-related database operations including:
    - Doctor existence checks
    - Doctor data extraction and formatting
    - Doctor-user relationship queries
    - Doctor profile validation
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_doctor_by_user(self, user: User) -> Optional[Medico]:
        """
        Get the doctor profile associated with a user.
        
        Args:
            user: The user to get doctor profile for
            
        Returns:
            Medico: The doctor instance if found, None otherwise
        """
        self.logger.debug(f"DoctorRepository: Getting doctor for user {user.email}")
        
        try:
            doctor = user.medicos.first()
            if doctor:
                self.logger.debug(f"DoctorRepository: Found doctor with ID {doctor.id}")
            else:
                self.logger.debug("DoctorRepository: No doctor found for user")
            return doctor
        except Exception as e:
            self.logger.error(f"DoctorRepository: Error getting doctor for user: {e}")
            return None
    
    def create_doctor(self, user: User, doctor_data: Dict[str, Any]) -> Medico:
        """
        Create a new doctor profile and associate it with a user.
        
        Args:
            user: The user to associate with the doctor
            doctor_data: Dictionary containing doctor information
            
        Returns:
            Medico: The created doctor instance
            
        Raises:
            ValueError: If required data is missing
        """
        self.logger.info(f"DoctorRepository: Creating doctor for user {user.email}")
        
        # Extract doctor-specific fields
        doctor = Medico(
            nome_medico=doctor_data.get("nome_medico"),
            crm_medico=doctor_data.get("crm_medico"),
            cns_medico=doctor_data.get("cns_medico"),
            estado=doctor_data.get("estado"),
            especialidade=doctor_data.get("especialidade")
        )
        doctor.save()
        
        # Associate with user
        user.medicos.add(doctor)
        
        self.logger.info(f"DoctorRepository: Created doctor with ID {doctor.id}")
        return doctor
    
    def update_doctor(self, doctor: Medico, doctor_data: Dict[str, Any]) -> Medico:
        """
        Update an existing doctor profile.
        
        Args:
            doctor: The doctor instance to update
            doctor_data: Dictionary containing updated doctor information
            
        Returns:
            Medico: The updated doctor instance
        """
        self.logger.info(f"DoctorRepository: Updating doctor ID {doctor.id}")
        
        # Update fields if provided in data
        if "nome_medico" in doctor_data:
            doctor.nome_medico = doctor_data["nome_medico"]
        if "crm_medico" in doctor_data and not doctor.crm_medico:
            doctor.crm_medico = doctor_data["crm_medico"]
        if "cns_medico" in doctor_data and not doctor.cns_medico:
            doctor.cns_medico = doctor_data["cns_medico"]
        if "estado" in doctor_data and not doctor.estado:
            doctor.estado = doctor_data["estado"]
        if "especialidade" in doctor_data:
            doctor.especialidade = doctor_data["especialidade"]
        
        doctor.save()
        
        self.logger.info(f"DoctorRepository: Updated doctor ID {doctor.id}")
        return doctor
    
    def check_doctor_exists_by_crm(self, crm: str, estado: str) -> bool:
        """
        Check if a doctor with the given CRM and state already exists.
        
        Args:
            crm: CRM number
            estado: State abbreviation
            
        Returns:
            bool: True if doctor exists, False otherwise
        """
        self.logger.debug(f"DoctorRepository: Checking CRM {crm} in state {estado}")
        
        exists = Medico.objects.filter(crm_medico=crm, estado=estado).exists()
        
        self.logger.debug(f"DoctorRepository: CRM {crm}/{estado} exists: {exists}")
        return exists
    
    def check_doctor_exists_by_cns(self, cns: str) -> bool:
        """
        Check if a doctor with the given CNS already exists.
        
        Args:
            cns: CNS number
            
        Returns:
            bool: True if doctor exists, False otherwise
        """
        self.logger.debug(f"DoctorRepository: Checking CNS {cns}")
        
        exists = Medico.objects.filter(cns_medico=cns).exists()
        
        self.logger.debug(f"DoctorRepository: CNS {cns} exists: {exists}")
        return exists
    
    def get_doctors_by_clinic(self, clinic) -> QuerySet:
        """
        Get all doctors associated with a specific clinic.
        
        Args:
            clinic: The clinic instance
            
        Returns:
            QuerySet: QuerySet of doctor instances
        """
        self.logger.debug(f"DoctorRepository: Getting doctors for clinic {clinic.id}")
        
        doctors = clinic.medicos.all()
        count = doctors.count()
        
        self.logger.debug(f"DoctorRepository: Found {count} doctors for clinic")
        return doctors
    
    def extract_doctor_data(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract doctor-specific data from a larger form data dictionary.
        
        Args:
            form_data: The complete form data dictionary
            
        Returns:
            dict: Dictionary containing only doctor data fields
        """
        self.logger.debug("DoctorRepository: Extracting doctor data from form")
        
        # Define doctor-specific fields
        doctor_fields = [
            'nome_medico', 'nome', 'crm_medico', 'crm', 'cns_medico', 'cns', 
            'estado', 'especialidade'
        ]
        
        # Extract and normalize field names
        doctor_data = {}
        extracted_count = 0
        
        for field in doctor_fields:
            if field in form_data:
                # Normalize field names to match model
                if field == 'nome':
                    doctor_data['nome_medico'] = form_data[field]
                elif field == 'crm':
                    doctor_data['crm_medico'] = form_data[field]
                elif field == 'cns':
                    doctor_data['cns_medico'] = form_data[field]
                else:
                    doctor_data[field] = form_data[field]
                extracted_count += 1
        
        self.logger.debug(f"DoctorRepository: Extracted {extracted_count} doctor fields")
        return doctor_data
    
    def check_crm_conflict(self, crm: str, estado: str, exclude_doctor_id: Optional[int] = None):
        """
        Check for CRM conflicts excluding a specific doctor.
        Uses the same logic as the original form validation.
        """
        return Medico.objects.filter(
            crm_medico=crm, 
            estado=estado
        ).exclude(
            id=exclude_doctor_id if exclude_doctor_id else None
        ).first()
    
    def check_cns_conflict(self, cns: str, exclude_doctor_id: Optional[int] = None):
        """
        Check for CNS conflicts excluding a specific doctor.
        Uses the same logic as the original form validation.
        """
        return Medico.objects.filter(cns_medico=cns).exclude(
            id=exclude_doctor_id if exclude_doctor_id else None
        ).first()
    
    def check_email_exists(self, email: str) -> bool:
        """
        Check if email already exists in User table.
        
        Args:
            email: The email address to check
            
        Returns:
            bool: True if email exists, False otherwise
        """
        self.logger.debug(f"DoctorRepository: Checking if email exists: {email}")
        
        exists = User.objects.filter(email=email).exists()
        self.logger.debug(f"DoctorRepository: Email {email} exists: {exists}")
        return exists