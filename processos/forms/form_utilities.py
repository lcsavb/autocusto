"""
Form Utilities - UI helpers and conditional field logic

This module contains utility functions for form display and conditional field management.
These functions handle UI concerns like CSS class management and conditional field visibility.
"""

import logging

logger = logging.getLogger('processos')


def mostrar_med(mostrar, *args):
    """
    Dynamically controls medication tab visibility in the UI based on existing process data.
    
    This function determines which medication tabs should be visible in the form interface.
    By default, all medication tabs except the first one are hidden (using Bootstrap's 'd-none' class).
    When editing an existing process, this function reveals tabs for medications that are already
    associated with the process, ensuring users can see and edit existing medication data.
    
    Args:
        mostrar (bool): Whether to show medications (True for editing existing process, False for new)
        *args: Variable arguments, where args[0] should be a Processo instance when mostrar=True
    
    Returns:
        dict: CSS class mapping for medication tabs ('d-none' to hide, '' to show)
    """
    # Initialize all medication tabs as hidden except med1 (which is always shown)
    dic = {
        "med2_mostrar": "d-none",
        "med3_mostrar": "d-none", 
        "med4_mostrar": "d-none",
    }
    
    if mostrar:
        # Get process from arguments
        processo = args[0]
        n = 1
        # Iterate through existing medications and reveal corresponding tabs
        # This ensures users can see all medications already associated with the process
        for med in processo.medicamentos.all():
            dic[f"med{n}_mostrar"] = ""  # Remove 'd-none' class to show the tab
            n = n + 1
    return dic


def ajustar_campos_condicionais(dados_paciente):
    """
    Conditionally shows/hides form fields based on patient data and form completion context.
    
    This function implements complex business logic for Brazilian medical form regulations:
    1. If patient has email, it means the form is being filled digitally by a doctor (not patient)
    2. If patient is incapable (incapaz), a responsible person's name field must be shown
    3. Campo 18 refers to specific SUS (Brazilian health system) form fields that are only
       required when the form is filled by medical personnel rather than the patient
    
    Args:
        dados_paciente (dict): Patient data dictionary containing form field values
    
    Returns:
        tuple: (visibility_dict, modified_patient_data)
            - visibility_dict: CSS classes to show/hide conditional fields
            - modified_patient_data: Updated patient data with 'preenchido_por' field set
    """
    # Initialize all conditional fields as hidden by default
    dic = {"responsavel_mostrar": "d-none", "campo_18_mostrar": "d-none"}
    
    # Business rule: If patient has email, assume doctor is filling the form digitally
    # This triggers showing additional SUS form fields (campo 18) required for medical personnel
    if dados_paciente["email_paciente"] != "":
        dic["campo_18_mostrar"] = ""  # Show campo 18 fields
        dados_paciente["preenchido_por"] = "medico"  # Set form completion context
    
    # Legal requirement: If patient is incapable, must show responsible person field
    if dados_paciente["incapaz"]:
        dic["responsavel_mostrar"] = ""  # Show responsible person name field
    
    return dic, dados_paciente