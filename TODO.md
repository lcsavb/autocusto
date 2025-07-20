

FOR EARLY DEPLOYMENT

when the medicamento is nenhum it works
recuperacao da senha instrucoes em ingles
instituir autenticação de dois fatores obrigatória
The pdfs_base directories exist for some protocols but not for epilepsia. Let me check if it should exist:
add copaxone for ms




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


 