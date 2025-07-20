

FOR EARLY DEPLOYMENT

when the medicamento is nenhum it works
remove cid mask
add renovacao rapida progress bar
recuperacao da senha instrucoes em ingles
instituir autenticação de dois fatores obrigatória
The pdfs_base directories exist for some protocols but not for epilepsia. Let me check if it should exist:





-----------------------------------------------------------------------------------------------------------------
integracao api cnes
js folders duplicated staticroot and staticroot/processos
erase duplicated old files (on drive pdf management)dd
put entire base pdfs in ram
roadmap
Finish front/backend test coverage
Finish frontend prescription test
change the variables to englishis
prescrições a vencer
modal pdf -> imprimir diretamente
saving pdfs and removing them
when trying to add a duplicated process a html response is being generated, not a json
add custom pdf files

  Code Quality

  - Remove debug prints from manejo_pdfs.py - replace with proper logging
  - Error handling in PDF generation - catch specific exceptions instead of broad try/catch
  - Consolidate JavaScript files - merge /static_root/js/med.js and /static_root/processos/js/med.js

  Security

  - Validate file paths in PDF serving to prevent directory traversal
  - Add rate limiting to password reset functionality
  - Sanitize user inputs in error reporting forms

  Performance

  - Cache medication choices instead of querying database repeatedly
  - Optimize form validation - avoid processing all 4 medications when only 1-2 are used
  - Use database indexing on frequently queried fields (CPF, CID)

  User Experience

  - Add loading states during PDF generation (can take time)
  - Improve error messages - make them more user-friendly
  - Add field validation hints before form submission
  - Implement auto-save for long forms

  Code Organization

  - Extract constants - move hardcoded values to settings
  - Create service layer for PDF operations
  - Add type hints to Python functions
  - Standardize naming - mix of Portuguese/English is confusing

  Most critical: logging system and JavaScript consolidation.


● Complete Summary: Data-Driven PDF Generation Implementation

  Current Problems

  1. Two parallel PDF systems: Legacy GeradorPDF (disk-based) + Modern GeradorPDFMemory (memory-based)
  2. Hardcoded disease classes: Separate class for each disease (Dor, EscleroseMultipla, etc.) with massive switch statements
  3. Hardcoded conditional fields: seletor_campos() function with giant if/elif chains for each disease
  4. Unmaintainable: Adding 1000 diseases would require 1000 classes + 1000 hardcoded field definitions

  Proposed Solution: Unified Data-Driven Architecture

  1. Single Unified PDF Generator

  - Rename: GeradorPDFMemory → GeradorPDF
  - Keep: All existing memory-based PDF operations (UTF-8 handling, RAM disk, concatenation)
  - Add: Strategy pattern support for disease/medication-specific files

  2. Universal PDF Handling (stays in main generator)

  The main GeradorPDF continues to handle:
  - ✅ Base LME form (always)
  - ✅ Consent PDF (if primeira_vez = True)
  - ✅ Report PDF (if relatorio = True)
  - ✅ Exam PDF (if exames = True)

  3. Data-Driven Strategy (NEW)

  Single strategy class that reads configuration from database:
  class DataDrivenStrategy:
      def get_disease_specific_paths(self, dados):
          # Returns paths like: ["pdfs_base/edss.pdf", "pdfs_base/lanns.pdf"]

      def get_medication_specific_paths(self, dados):
          # Returns paths like: ["fingolimod_monitoring.pdf"]

  4. Database Configuration (NEW)

  Store everything in Protocolo.dados_condicionais JSON field:
  {
    "fields": [
      {"name": "opt_edss", "type": "choice", "choices": ["0", "1", "2"...]}
    ],
    "disease_files": ["pdfs_base/edss.pdf"],
    "medications": {
      "fingolimode": ["fingolimod_monitoring.pdf"],
      "natalizumabe": ["natalizumab_specific.pdf"]
    }
  }

  5. Directory Structure Leverage

  Use existing filesystem structure:
  static/autocusto/protocolos/esclerose_multipla/
  ├── consentimento.pdf (handled by main generator)
  ├── pdfs_base/
  │   ├── edss.pdf (disease-specific - strategy)
  │   └── relatorio.pdf (universal - main generator)
  └── fingolimod_monitoring.pdf (medication-specific - strategy)

  Implementation Changes

  Files to Modify:

  1. processos/manejo_pdfs_memory.py:
    - Rename class GeradorPDFMemory → GeradorPDF
    - Add strategy pattern integration
    - Keep all existing universal logic
  2. processos/pdf_strategies.py (NEW):
    - Create DataDrivenStrategy class
    - Database-driven path resolution
  3. processos/forms.py:
    - Replace seletor_campos() with database lookup
    - Use protocolo.dados_condicionais["fields"]
  4. processos/views.py:
    - Update import from GeradorPDFMemory to GeradorPDF

  Database Updates:

  1. Populate Protocolo.dados_condicionais for existing diseases:
    - Multiple Sclerosis: EDSS + medication configs
    - Chronic Pain: LANNS + EVA + medication configs
    - Epilepsy: medication configs
    - etc.

  Legacy Code:

  1. Keep logica_raw/ intact (for reference/backup)
  2. Gradually deprecate disease-specific classes
  3. No immediate deletion - parallel systems during transition

  Benefits

  1. Single PDF Generator: One unified class instead of parallel systems
  2. Data-Driven: Add new diseases through database config, not code
  3. Maintainable: No more giant switch statements
  4. Preserves Logic: All existing functionality maintained
  5. Directory Leveraged: Filesystem structure drives behavior
  6. Gradual Migration: Can implement disease by disease

  Migration Path

  1. ✅ Start with Multiple Sclerosis (most complex medication logic)
  2. Create database configuration for MS
  3. Test PDF generation matches existing behavior
  4. Migrate other diseases one by one
  5. Eventually deprecate legacy system

  This approach eliminates the 1000 disease classes problem while preserving all existing functionality and leveraging your current directory structure.