"""
Form Validators - Extracted validation logic with simplified control flow

This module contains validator classes that handle complex validation logic
that was previously embedded in form clean() methods. The validators use
early returns and clear error handling to avoid nested control flow hell.
"""

import logging
from typing import List, Set

logger = logging.getLogger(__name__)


class MedicationValidator:
    """
    Validator class for medication form fields with simplified control flow.
    
    This class extracts the complex medication validation logic from NovoProcesso.clean()
    and provides a clean, testable interface with early returns and clear error handling.
    """
    
    def __init__(self, form_data: dict):
        """
        Initialize validator with form data.
        
        Args:
            form_data: Dictionary of form field data from request.POST
        """
        self.form_data = form_data
        self.submitted_fields = set(form_data.keys()) if form_data else set()
        logger.debug(f"MedicationValidator initialized with {len(self.submitted_fields)} submitted fields")
    
    def get_submitted_medications(self) -> List[int]:
        """
        Extract list of medication numbers that were actually submitted with valid data.
        
        Uses early returns to avoid nested conditionals and clearly identifies
        which medications have meaningful data vs empty/placeholder values.
        
        Returns:
            List[int]: List of medication numbers (1-4) that have valid data
        """
        submitted_med_ids = []
        
        for i in range(1, 5):
            med_id_field = f"id_med{i}"
            
            # Skip if field not in submitted data
            if med_id_field not in self.submitted_fields:
                continue
            
            med_id_value = self.form_data.get(med_id_field)
            
            # Check for various forms of "empty" medication selections
            if self._is_empty_medication_value(med_id_value):
                logger.debug(f"Medication {i} has empty value '{med_id_value}' - skipping")
                continue
            
            # Valid medication found
            submitted_med_ids.append(i)
            logger.debug(f"Found valid submitted medication {i}: {med_id_value}")
        
        logger.info(f"Found {len(submitted_med_ids)} submitted medications: {submitted_med_ids}")
        return submitted_med_ids
    
    def validate_medication(self, med_num: int, form) -> bool:
        """
        Validate all fields for a specific medication number.
        
        Uses early validation pattern to check each requirement separately
        and add specific error messages for each failure case.
        
        Args:
            med_num: Medication number (1-4) to validate
            form: Django form instance to add errors to
            
        Returns:
            bool: True if medication is valid, False if validation errors found
        """
        logger.debug(f"Validating medication {med_num}")
        is_valid = True
        
        # Validate main medication selection
        if not self._validate_medication_selection(med_num, form):
            is_valid = False
        
        # Validate repetir posologia field
        if not self._validate_repetir_posologia(med_num, form):
            is_valid = False
        
        # Validate dosage and quantity fields for all 6 months
        if not self._validate_dosage_and_quantities(med_num, form):
            is_valid = False
        
        logger.debug(f"Medication {med_num} validation result: {'VALID' if is_valid else 'INVALID'}")
        return is_valid
    
    def cleanup_unused_medication_errors(self, form, submitted_medications: List[int]) -> None:
        """
        Remove validation errors for medications that were not submitted.
        
        This prevents Django from showing validation errors for optional
        medication fields that the user didn't intend to fill out.
        
        Args:
            form: Django form instance to clean up
            submitted_medications: List of medication numbers that were submitted
        """
        logger.debug("Cleaning up validation errors for unused medications")
        
        for i in range(1, 5):
            if i not in submitted_medications:
                self._remove_medication_errors(i, form)
    
    def _is_empty_medication_value(self, med_id_value: str) -> bool:
        """Check if medication value represents an empty/placeholder selection."""
        if not med_id_value:
            return True
        
        if not med_id_value.strip():
            return True
        
        # Check for common placeholder values
        empty_values = ["nenhum", "none", "", "null", "undefined"]
        return med_id_value.strip().lower() in empty_values
    
    def _validate_medication_selection(self, med_num: int, form) -> bool:
        """Validate that a medication was actually selected."""
        med_id_field = f"id_med{med_num}"
        med_id_value = self.form_data.get(med_id_field)
        
        if not med_id_value or not med_id_value.strip():
            form.add_error(None, f"Medicamento {med_num}: Seleção do medicamento é obrigatória")
            logger.debug(f"Medication {med_num}: Missing medication selection")
            return False
        
        return True
    
    def _validate_repetir_posologia(self, med_num: int, form) -> bool:
        """Validate that repetir posologia field is filled."""
        repetir_field = f"med{med_num}_repetir_posologia"
        
        if repetir_field not in self.submitted_fields:
            form.add_error(None, f"Medicamento {med_num}: Campo 'repetir posologia' deve ser preenchido")
            logger.debug(f"Medication {med_num}: Missing repetir posologia field")
            return False
        
        return True
    
    def _validate_dosage_and_quantities(self, med_num: int, form) -> bool:
        """Validate dosage and quantity fields for all 6 months."""
        missing_fields = []
        
        for month in range(1, 7):
            posologia_field = f"med{med_num}_posologia_mes{month}"
            qtd_field = f"qtd_med{med_num}_mes{month}"
            
            # Check posologia field
            if not self._is_field_filled(posologia_field):
                missing_fields.append(f"posologia mês {month}")
            
            # Check quantity field
            if not self._is_field_filled(qtd_field):
                missing_fields.append(f"quantidade mês {month}")
        
        # Add summary error if any fields are missing
        if missing_fields:
            form.add_error(None, f"Medicamento {med_num}: Todos os campos de posologia e quantidade (6 meses) devem ser preenchidos")
            logger.debug(f"Medication {med_num}: Missing fields: {missing_fields}")
            return False
        
        return True
    
    def _is_field_filled(self, field_name: str) -> bool:
        """Check if a field is present and has a non-empty value."""
        if field_name not in self.submitted_fields:
            return False
        
        field_value = self.form_data.get(field_name)
        return field_value and field_value.strip()
    
    def _remove_medication_errors(self, med_num: int, form) -> None:
        """Remove all validation errors for a specific medication number."""
        logger.debug(f"Removing validation errors for unused medication {med_num}")
        
        # Remove main medication field errors
        med_id_field = f"id_med{med_num}"
        if med_id_field in form.errors:
            del form.errors[med_id_field]
        
        # Remove repetir posologia errors
        repetir_field = f"med{med_num}_repetir_posologia"
        if repetir_field in form.errors:
            del form.errors[repetir_field]
        
        # Remove dosage and quantity field errors for all months
        for month in range(1, 7):
            posologia_field = f"med{med_num}_posologia_mes{month}"
            qtd_field = f"qtd_med{med_num}_mes{month}"
            
            if posologia_field in form.errors:
                del form.errors[posologia_field]
            if qtd_field in form.errors:
                del form.errors[qtd_field]