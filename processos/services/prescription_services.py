"""
Prescription Services - Backward Compatibility Module

This module provides backward compatibility imports for the refactored prescription services.
The original 802-line prescription_services.py has been broken down into focused, single-responsibility services.

New Architecture:
- PrescriptionDataFormatter → prescription/data_formatting.py (60 lines)  
- PrescriptionTemplateSelector → prescription/template_selection.py (130 lines)
- PrescriptionPDFService → prescription/pdf_generation.py (110 lines)
- PrescriptionService → prescription/workflow_service.py (160 lines)
- RenewalService → prescription/renewal_service.py (255 lines)

Import from this module to maintain compatibility with existing code.
"""

# Import all services from the new prescription package
from .prescription import (
    PrescriptionDataFormatter,
    PrescriptionTemplateSelector,
    PrescriptionPDFService,
    PrescriptionService,
    RenewalService,
)

# Maintain backward compatibility - all existing imports should continue to work
__all__ = [
    'PrescriptionDataFormatter',
    'PrescriptionTemplateSelector', 
    'PrescriptionPDFService',
    'PrescriptionService',
    'RenewalService',
]