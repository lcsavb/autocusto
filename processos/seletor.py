from django import forms

REPETIR_ESCOLHAS = [(True, "Sim"), (False, "Não")]


def gerador_escolhas_numericas(min_n, max_n):
    ESCOLHAS = []
    while min_n <= max_n:
        ESCOLHAS.append((min_n, min_n))
        min_n += 1
    return ESCOLHAS


# Legacy seletor_campos function removed - all protocols now use data-driven approach
# Migrated protocols: esclerose_multipla, dor_cronica, doenca_de_alzheimer
# Remaining protocols will be migrated to use dados_condicionais JSONField

def seletor_campos(protocolo):
    """
    DEPRECATED: Legacy function for hardcoded conditional fields.
    
    This function has been replaced by the data-driven approach using 
    the dados_condicionais JSONField in the Protocolo model.
    
    All new protocols should be configured using management commands
    that populate the dados_condicionais field instead of adding
    hardcoded logic here.
    
    Migrated protocols: esclerose_multipla, dor_cronica, doenca_de_alzheimer
    Remaining protocols: 78 (to be migrated)
    """
    # Return empty dict - migrated protocols use get_conditional_fields()
    # from pdf_strategies.py which reads dados_condicionais JSONField
    return {}
