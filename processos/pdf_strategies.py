# -*- coding: utf-8 -*-
"""
Data-driven PDF generation strategy that reads configuration from database.
Only handles disease-specific and medication-specific PDFs.
Universal PDFs (consent, report, exams) are handled by main GeradorPDF.
"""

import os
from django.conf import settings
from processos.models import Protocolo
from processos.paths import get_static_path


class DataDrivenStrategy:
    """
    Universal strategy that reads PDF configuration from database.
    Only returns disease-specific and medication-specific PDF paths.
    """
    
    def __init__(self, protocolo):
        self.protocolo = protocolo
        print(f"DEBUG: DataDrivenStrategy initialized for {protocolo.nome}")
    
    def get_disease_specific_paths(self, dados_lme_base):
        """Get disease-specific PDF paths (like EDSS scale for MS)"""
        try:
            config = self.protocolo.dados_condicionais or {}
            disease_files = config.get("disease_files", [])
            
            paths = []
            for file_path in disease_files:
                full_path = get_static_path("protocolos", self.protocolo.nome, file_path)
                if os.path.exists(full_path):
                    paths.append(full_path)
                    print(f"DEBUG: Added disease file: {file_path}")
                else:
                    print(f"WARNING: Disease file not found: {full_path}")
            
            return paths
            
        except Exception as e:
            print(f"ERROR: Failed to get disease-specific paths: {e}")
            return []
    
    def get_medication_specific_paths(self, dados_lme_base):
        """Get medication-specific PDF paths (like Fingolimod monitoring)"""
        try:
            config = self.protocolo.dados_condicionais or {}
            medications = config.get("medications", {})
            
            medicamento = dados_lme_base.get("med1", "").lower()
            print(f"DEBUG: Processing medication: {medicamento}")
            
            # Find matching medication in config
            med_config = None
            for med_key, med_data in medications.items():
                if med_key in medicamento:
                    med_config = med_data
                    print(f"DEBUG: Found medication config for {med_key}")
                    break
            
            if not med_config:
                print(f"DEBUG: No specific config found for medication: {medicamento}")
                return []
            
            # Get medication-specific files
            paths = []
            med_files = med_config.get("files", [])
            
            for file_path in med_files:
                full_path = get_static_path("protocolos", self.protocolo.nome, file_path)
                if os.path.exists(full_path):
                    paths.append(full_path)
                    print(f"DEBUG: Added medication file: {file_path}")
                else:
                    print(f"WARNING: Medication file not found: {full_path}")
            
            return paths
            
        except Exception as e:
            print(f"ERROR: Failed to get medication-specific paths: {e}")
            return []


def get_conditional_fields(protocolo):
    """
    Extract conditional form fields from protocol database configuration.
    Replaces the hardcoded seletor_campos() function.
    """
    try:
        config = protocolo.dados_condicionais or {}
        fields_config = config.get("fields", [])
        
        if not fields_config:
            return {}
        
        print(f"DEBUG: Found {len(fields_config)} conditional fields for {protocolo.nome}")
        
        # Convert database field configuration to Django form fields
        from django import forms
        
        campos = {}
        for field_config in fields_config:
            field_name = field_config["name"]
            field_type = field_config["type"]
            label = field_config["label"]
            required = field_config.get("required", False)
            widget_class = field_config.get("widget_class", "form-control")
            
            if field_type == "choice":
                campo = forms.ChoiceField(
                    label=label,
                    initial=field_config.get("initial", ""),
                    choices=field_config["choices"],
                    required=required,
                    widget=forms.Select(attrs={"class": widget_class})
                )
                campos[field_name] = campo
                print(f"DEBUG: Created choice field: {field_name}")
                
            elif field_type == "boolean":
                campo = forms.BooleanField(
                    label=label,
                    required=required,
                    initial=field_config.get("initial", False),
                    widget=forms.CheckboxInput(attrs={"class": widget_class})
                )
                campos[field_name] = campo
                print(f"DEBUG: Created boolean field: {field_name}")
                
            elif field_type == "number":
                campo = forms.FloatField(
                    label=label,
                    required=required,
                    initial=field_config.get("initial"),
                    widget=forms.NumberInput(attrs={"class": widget_class, "step": "any"})
                )
                campos[field_name] = campo
                print(f"DEBUG: Created number field: {field_name}")
                
            elif field_type == "text":
                campo = forms.CharField(
                    label=label,
                    required=required,
                    initial=field_config.get("initial", ""),
                    widget=forms.TextInput(attrs={"class": widget_class})
                )
                campos[field_name] = campo
                print(f"DEBUG: Created text field: {field_name}")
                
            elif field_type == "textarea":
                campo = forms.CharField(
                    label=label,
                    required=required,
                    initial=field_config.get("initial", ""),
                    widget=forms.Textarea(attrs={"class": widget_class, "rows": 4})
                )
                campos[field_name] = campo
                print(f"DEBUG: Created textarea field: {field_name}")
                
            elif field_type == "date":
                campo = forms.DateField(
                    label=label,
                    required=required,
                    initial=field_config.get("initial"),
                    widget=forms.DateInput(attrs={"class": widget_class, "type": "date"})
                )
                campos[field_name] = campo
                print(f"DEBUG: Created date field: {field_name}")
                
            else:
                print(f"WARNING: Unknown field type '{field_type}' for field '{field_name}'")
        
        return campos
        
    except Exception as e:
        print(f"ERROR: Failed to get conditional fields: {e}")
        return {}