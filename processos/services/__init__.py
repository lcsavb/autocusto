"""
Services Package - Business Logic Layer

This package contains all service classes that handle business logic, data processing,
and infrastructure operations. Services are organized by domain responsibility.

Available Services:

Business Logic Services:
- RegistrationService: Process and patient registration logic
- PrescriptionService: Complete prescription workflow management
- RenewalService: Prescription renewal business logic
- PrescriptionPDFService: PDF generation coordination
- PrescriptionViewSetupService: View setup and data preparation

Infrastructure Services:
- PDFGenerator: Pure PDF technical operations
- PDFResponseBuilder: HTTP response creation for PDFs
- PDFFileService: File I/O operations for PDFs

Strategy Services:
- DataDrivenStrategy: Protocol-based template selection
"""