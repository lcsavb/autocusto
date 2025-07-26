"""
Base Forms - Common form patterns and mixins

This module contains base classes and mixins for common form functionality:
- PrescriptionBaseMixin: Common patterns for prescription forms
- Form helpers and utilities shared across multiple form classes
"""

from django import forms


class PrescriptionBaseMixin:
    """
    Mixin for prescription forms with common functionality.
    
    This mixin provides shared functionality for prescription forms including
    error handling patterns, field setup, and common validation helpers.
    """
    
    def add_medication_error(self, medication_num: int, message: str):
        """
        Add a medication-specific error message.
        
        Args:
            medication_num: The medication number (1-4)
            message: Error message to display
        """
        self.add_error(None, f"Medicamento {medication_num}: {message}")
    
    def setup_form_styling(self):
        """Apply consistent styling to form fields."""
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect, forms.ClearableFileInput)):
                current_class = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = current_class + ' form-control'
            field.widget.attrs['data-crispy-field'] = 'true'