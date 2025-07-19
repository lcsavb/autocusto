
# Paths básicos
# English: PATH_LME_BASE
# PATH_LME_BASE = os.path.join(BASE_DIR, 'static_root', 'lme_base_modelo.pdf')

# SECURITY FIX: Secure PDF generation directory (not publicly accessible)
# English: PATH_SECURE_PDF_DIR
def get_secure_pdf_path():
    """Returns the secure path for PDF generation with debug logging."""
    from django.conf import settings
    import os
    
    secure_path = os.path.join(settings.BASE_DIR, "processos", "pdf")
    print(f"DEBUG: Secure PDF path configured as: {secure_path}")
    print(f"DEBUG: Secure PDF path exists: {os.path.exists(secure_path)}")
    
    # Ensure directory exists
    os.makedirs(secure_path, exist_ok=True)
    print(f"DEBUG: Created secure PDF directory: {secure_path}")
    
    return secure_path

PATH_SECURE_PDF_DIR = get_secure_pdf_path()

import os
from django.conf import settings

def get_static_path(*args):
    """Get static file path that works in both development and production"""
    if settings.DEBUG:
        return os.path.join(settings.BASE_DIR, "static", "autocusto", *args)
    else:
        return os.path.join(settings.STATIC_ROOT, *args)

# English: PATH_EXAMS
PATH_EXAMES = get_static_path("processos", "exames_base_modelo.pdf")
# English: PATH_REPORT
PATH_RELATORIO = get_static_path("processos", "relatorio_modelo.pdf")
# English: PATH_RCE
PATH_RCE = get_static_path("processos", "rce_modelo.pdf")

# Artrite Reumatóide
# English: PATH_REPORT_RA
PATH_RELATORIO_AR = get_static_path("processos", "artrite_reumatoide", "relatorio_modelo.pdf")
# English: PATH_RA_CONSENT
PATH_AR_CONSENTIMENTO = get_static_path("processos", "artrite_reumatoide", "consentimento_modelo.pdf")

# Doença de Alzheimer
# English: PATH_MEEM
PATH_MEEM = get_static_path("processos", "alzheimer", "meem_modelo.pdf")
# English: PATH_CDR
PATH_CDR = get_static_path("processos", "alzheimer", "cdr_modelo.pdf")
# English: PATH_DA_CONSENT
PATH_DA_CONSENTIMENTO = get_static_path("processos", "alzheimer", "consentimento_modelo.pdf")


# Esclerose Múltipla
# English: PATH_EDSS
PATH_EDSS = get_static_path("processos", "esclerose_multipla", "edss_modelo.pdf")
# English: PATH_MS_CONSENT
PATH_EM_CONSENTIMENTO = get_static_path("processos", "esclerose_multipla", "consentimento.pdf")
# English: PATH_FINGO_MONIT
PATH_FINGO_MONIT = get_static_path("processos", "esclerose_multipla", "monitoramento_fingolimode_modelo.pdf")
# English: PATH_NATA_EXAMS
PATH_NATA_EXAMES = get_static_path("processos", "esclerose_multipla", "exames_nata_modelo.pdf")


# Epilepsia
# English: PATH_EPILEPSY_CONSENT
PATH_EPILEPSIA_CONSENTIMENTO = get_static_path("processos", "epilepsia", "consentimento_g400.pdf")

# Dislipidemia
# English: PATH_DYSLIPIDEMIA_CONSENT
PATH_DISLIPIDEMIA_CONSENTIMENTO = get_static_path("processos", "dislipidemia", "consentimento_modelo.pdf")

# Dor
# English: PATH_PAIN_CONSENT
PATH_DOR_CONSENTIMENTO = get_static_path("processos", "dor", "consentimento_modelo.pdf")
# English: PATH_PAIN_SCALE
PATH_DOR_ESCALA = get_static_path("processos", "dor", "escala_modelo.pdf")
