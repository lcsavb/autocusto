

from paths import (
    PATH_EDSS,
    PATH_EM_CONSENTIMENTO,
    PATH_EXAMES,
    PATH_FINGO_MONIT,
    PATH_RELATORIO,
    PATH_NATA_EXAMES,
)
from dados import PATH_PDF_FINAL
from manejo_pdfs import (
    GeradorPDF,
    remover_pdfs_intermediarios,
    preencher_formularios,
    gerar_pdf_final,
)


# multiple sclerosis
class EscleroseMultipla(GeradorPDF):
    def __init__(self, dados_lme_base, dados_condicionais, path_lme_base):
        GeradorPDF.__init__(self, dados_lme_base, dados_condicionais, path_lme_base)
        self.dados_condicionais = dados_condicionais

    # renew
    def renovar(self, dados_lme_base, dados_condicionais, path_lme_base):
        """Handles prescription renewal for multiple sclerosis patients.
        
        This method processes renewal requests for MS medications by merging
        base prescription data with conditional fields and routing to specific
        medication protocols based on the selected medication.
        
        Args:
            dados_lme_base (dict): Base prescription data (patient, doctor, clinic info)
            dados_condicionais (dict): Disease-specific conditional fields
            path_lme_base (str): Path to base LME PDF template
            
        Returns:
            str: Path to generated PDF file
            
        Critique:
        - The function has complex nested logic that could be refactored
        - Medication routing logic is hardcoded and not easily extensible
        - Error handling is minimal - should validate medication types
        - The function mixes data processing with PDF generation concerns
        
        Suggested Improvements:
        - Extract medication routing to a separate strategy pattern
        - Add input validation for required fields
        - Consider using a medication registry instead of hardcoded if/elif
        - Add logging for debugging prescription generation issues
        """
        dados_lme_base.update(dados_condicionais)
        dados_finais = dados_lme_base
        medicamento = dados_finais["med1"].lower()

        arquivos_modelo = [path_lme_base, PATH_EDSS]

        arquivos_base = preencher_formularios(arquivos_modelo, dados_finais)

        if "fingolimode" in medicamento:
            arquivos_condicionais = fingolimode_renova(dados_finais)
            arquivos = arquivos_base + arquivos_condicionais
        elif "betainterferon" in medicamento:
            arquivos_condicionais = betainterferon_renova(dados_finais)
            arquivos = arquivos_base + arquivos_condicionais
        elif "natalizumabe" in medicamento:
            arquivos_condicionais = natalizumabe_renova(dados_finais)
            arquivos = arquivos_base + arquivos_condicionais
        elif "fumarato" in medicamento:
            arquivos_condicionais = fumarato_renova(dados_finais)
            arquivos = arquivos_base + arquivos_condicionais
        elif "glatiramer" in medicamento:
            arquivos_condicionais = glatiramer_renova(dados_finais)
            arquivos = arquivos_base + arquivos_condicionais
        elif "teriflunomida" in medicamento:
            arquivos_condicionais = teriflunomida_renova(dados_finais)
            arquivos = arquivos_base + arquivos_condicionais
        elif "azatioprina" in medicamento:
            arquivos_condicionais = azatioprina_renova(dados_finais)
            arquivos = arquivos_base + arquivos_condicionais

        pdf_em = gerar_pdf_final(arquivos, PATH_PDF_FINAL)
        # Remover arquivos intermediários
        remover_pdfs_intermediarios(*arquivos)
        return pdf_em

    # first time
    def primeira_vez(self, dados_lme_base, dados_condicionais, path_lme_base):
        """Handles first-time prescription for multiple sclerosis patients.
        
        This method processes initial prescription requests for MS medications,
        typically requiring more extensive documentation and exam requirements
        compared to renewals.
        
        Args:
            dados_lme_base (dict): Base prescription data
            dados_condicionais (dict): Disease-specific conditional fields  
            path_lme_base (str): Path to base LME PDF template
            
        Returns:
            str: Path to generated PDF file
            
        Critique:
        - Similar routing complexity as renovar() method
        - Duplicated medication handling logic between primeira_vez and renovar
        - No clear separation between first-time vs renewal requirements
        
        Suggested Improvements:
        - Create shared medication handler base class
        - Define clear interfaces for first-time vs renewal differences
        - Extract common PDF generation logic to parent class
        """
        dados_lme_base.update(dados_condicionais)
        dados_finais = dados_lme_base
        medicamento = dados_finais["med1"].lower()
        emitir_exames = dados_finais["exames"]
        arquivos_modelo = [path_lme_base, PATH_EDSS]

        arquivos_base = preencher_formularios(arquivos_modelo, dados_finais)

        if "fingolimode" in medicamento:
            arquivos_condicionais = fingolimode_1vez(dados_finais)
            arquivos = arquivos_base + arquivos_condicionais
        elif "betainterferon" in medicamento and emitir_exames:
            arquivos_condicionais = betainterferon_1vez(dados_finais)
            arquivos = arquivos_base + arquivos_condicionais
        elif "natalizumabe" in medicamento:
            arquivos_condicionais = natalizumabe_1vez(dados_finais)
            arquivos = arquivos_base + arquivos_condicionais
        elif "fumarato" in medicamento:
            arquivos_condicionais = fumarato_1vez(dados_finais)
            arquivos = arquivos_base + arquivos_condicionais
        elif "glatiramer" in medicamento:
            arquivos_condicionais = glatiramer_1vez(dados_finais)
            arquivos = arquivos_base + arquivos_condicionais
        elif "teriflunomida" in medicamento:
            arquivos_condicionais = teriflunomida_1vez(dados_finais)
            arquivos = arquivos_base + arquivos_condicionais
        elif "azatioprina" in medicamento:
            arquivos_condicionais = azatioprina_1vez(dados_finais)
            arquivos = arquivos_base + arquivos_condicionais

        pdf_em = gerar_pdf_final(arquivos, PATH_PDF_FINAL)
        remover_pdfs_intermediarios(*arquivos)
        print(pdf_em)
        return pdf_em


# fingolimod first time
def fingolimode_1vez(dados_finais):
    """Generates fingolimod prescription documents for first-time patients.
    
    Fingolimod is a sphingosine 1-phosphate receptor modulator used for
    multiple sclerosis treatment. First-time prescriptions require specific
    monitoring protocols and cardiac evaluation forms.
    
    Args:
        dados_finais (dict): Complete patient and prescription data
        
    Returns:
        list: List of filled PDF file paths ready for concatenation
        
    Critique:
    - Function duplicates exam handling logic with other medication functions
    - Hardcoded path constants reduce flexibility
    - No input validation for required fingolimod-specific fields
    - Return type inconsistency (sometimes returns list, sometimes single file)
    
    Suggested Improvements:
    - Create MedicationProtocol base class with standard interface
    - Add validation for fingolimod contraindications
    - Implement consistent return types across all medication functions
    - Add dosing validation and drug interaction checks
    """
    emitir_exames = dados_finais["exames"]
    dados_finais["relatorio"] = dados_finais.pop("relatorio_fingolimode_1vez")
    if emitir_exames:
        dados_finais["exames_solicitados"] = dados_finais.pop("exames_em_1vez")
        arquivos_protocolo_1vez = [PATH_FINGO_MONIT, PATH_EXAMES]
        arquivos_preenchidos = preencher_formularios(
            arquivos_protocolo_1vez, dados_finais
        )
        return arquivos_preenchidos
    else:
        arquivos_protocolo_1vez = [PATH_FINGO_MONIT]
        arquivos_preenchidos = preencher_formularios(
            arquivos_protocolo_1vez, dados_finais
        )
        return arquivos_preenchidos


def fingolimode_renova(dados_finais):
    emitir_exames = dados_finais["exames"]
    if emitir_exames:
        dados_finais["exames_solicitados"] = dados_finais.pop("exames_em_renova")
        arquivos_protocolo_renovacao = [PATH_EXAMES]
        arquivos_preenchidos = preencher_formularios(
            arquivos_protocolo_renovacao, dados_finais
        )
        return arquivos_preenchidos

    else:
        return None


def natalizumabe_1vez(dados_finais):
    emitir_exames = dados_finais["exames"]
    dados_finais["relatorio"] = dados_finais.pop("relatorio_natalizumabe_1vez")
    dados_finais["consentimento_medicamento"] = "natalizumabe"
    if emitir_exames:
        arquivos_protocolo_1vez = [PATH_RELATORIO, PATH_EXAMES, PATH_EM_CONSENTIMENTO]
        dados_finais["exames_solicitados"] = dados_finais.pop("exames_em_1vez")
        arquivos_preenchidos = preencher_formularios(
            arquivos_protocolo_1vez, dados_finais
        )
        return arquivos_preenchidos
    else:
        arquivos_protocolo_1vez = [PATH_RELATORIO, PATH_EM_CONSENTIMENTO]
        arquivos_preenchidos = preencher_formularios(
            arquivos_protocolo_1vez, dados_finais
        )
        return arquivos_preenchidos


def natalizumabe_renova(dados_finais):
    emitir_exames = dados_finais["exames"]
    if emitir_exames:
        dados_finais["exames_solicitados"] = dados_finais.pop("exames_nata_renova")
        arquivos_protocolo_renovacao = [PATH_NATA_EXAMES]
        arquivos_preenchidos = preencher_formularios(
            arquivos_protocolo_renovacao, dados_finais
        )
        return arquivos_preenchidos

    else:
        return None


def betainterferon_1vez(dados_finais):
    emitir_exames = dados_finais["exames"]
    dados_finais["consentimento_medicamento"] = "betainterferona1a"
    if emitir_exames:
        arquivos_protocolo_1vez = [PATH_EXAMES, PATH_EM_CONSENTIMENTO]
        dados_finais["exames_solicitados"] = dados_finais.pop("exames_em_1vez")
        arquivos_preenchidos = preencher_formularios(
            arquivos_protocolo_1vez, dados_finais
        )
        return arquivos_preenchidos
    else:
        arquivos_protocolo_1vez = [PATH_EM_CONSENTIMENTO]
        arquivos_preenchidos = preencher_formularios(
            arquivos_protocolo_1vez, dados_finais
        )
        return arquivos_preenchidos


def betainterferon_renova(dados_finais):
    emitir_exames = dados_finais["exames"]
    if emitir_exames:
        dados_finais["exames_solicitados"] = dados_finais.pop("exames_em_renova")
        arquivos_protocolo_renovacao = [PATH_EXAMES]
        arquivos_preenchidos = preencher_formularios(
            arquivos_protocolo_renovacao, dados_finais
        )
        return arquivos_preenchidos

    else:
        return None


def fumarato_1vez(dados_finais):
    emitir_exames = dados_finais["exames"]
    dados_finais["relatorio"] = dados_finais.pop("relatorio_fumarato_1vez")
    dados_finais["consentimento_medicamento"] = "dimetila"
    if emitir_exames:
        dados_finais["exames_solicitados"] = dados_finais.pop("exames_em_1vez")
        arquivos_protocolo_1vez = [PATH_EXAMES, PATH_EM_CONSENTIMENTO, PATH_RELATORIO]
        arquivos_preenchidos = preencher_formularios(
            arquivos_protocolo_1vez, dados_finais
        )
        return arquivos_preenchidos
    else:
        arquivos_protocolo_1vez = [PATH_EM_CONSENTIMENTO, PATH_RELATORIO]
        arquivos_preenchidos = preencher_formularios(
            arquivos_protocolo_1vez, dados_finais
        )
        return arquivos_preenchidos


def fumarato_renova(dados_finais):
    emitir_exames = dados_finais["exames"]
    if emitir_exames:
        dados_finais["exames_solicitados"] = dados_finais.pop("exames_em_renova")
        arquivos_protocolo_renovacao = [PATH_EXAMES]
        arquivos_preenchidos = preencher_formularios(
            arquivos_protocolo_renovacao, dados_finais
        )
        return arquivos_preenchidos

    else:
        return None


def azatioprina_1vez(dados_finais):
    emitir_exames = dados_finais["exames"]
    dados_finais["consentimento_medicamento"] = "azatioprina"
    if emitir_exames:
        arquivos_protocolo_1vez = [PATH_EXAMES, PATH_EM_CONSENTIMENTO]
        dados_finais["exames_solicitados"] = dados_finais.pop("exames_em_1vez")
        arquivos_preenchidos = preencher_formularios(
            arquivos_protocolo_1vez, dados_finais
        )
        return arquivos_preenchidos
    else:
        arquivos_protocolo_1vez = [PATH_EM_CONSENTIMENTO]
        arquivos_preenchidos = preencher_formularios(
            arquivos_protocolo_1vez, dados_finais
        )
        return arquivos_preenchidos


def azatioprina_renova(dados_finais):
    emitir_exames = dados_finais["exames"]
    if emitir_exames:
        dados_finais["exames_solicitados"] = dados_finais.pop("exames_em_renova")
        arquivos_protocolo_renovacao = [PATH_EXAMES]
        arquivos_preenchidos = preencher_formularios(
            arquivos_protocolo_renovacao, dados_finais
        )
        return arquivos_preenchidos

    else:
        return None


def teriflunomida_1vez(dados_finais):
    emitir_exames = dados_finais["exames"]
    dados_finais["consentimento_medicamento"] = "teriflunomida"
    if emitir_exames:
        arquivos_protocolo_1vez = [PATH_EXAMES, PATH_EM_CONSENTIMENTO]
        dados_finais["exames_solicitados"] = dados_finais.pop("exames_em_1vez")
        arquivos_preenchidos = preencher_formularios(
            arquivos_protocolo_1vez, dados_finais
        )
        return arquivos_preenchidos
    else:
        arquivos_protocolo_1vez = [PATH_EM_CONSENTIMENTO]
        arquivos_preenchidos = preencher_formularios(
            arquivos_protocolo_1vez, dados_finais
        )
        return arquivos_preenchidos


def teriflunomida_renova(dados_finais):
    emitir_exames = dados_finais["exames"]
    if emitir_exames:
        dados_finais["exames_solicitados"] = dados_finais.pop("exames_em_renova")
        arquivos_protocolo_renovacao = [PATH_EXAMES]
        arquivos_preenchidos = preencher_formularios(
            arquivos_protocolo_renovacao, dados_finais
        )
        return arquivos_preenchidos

    else:
        return None


def glatiramer_1vez(dados_finais):
    emitir_exames = dados_finais["exames"]
    dados_finais["consentimento_medicamento"] = "glatiramer"
    if emitir_exames:
        arquivos_protocolo_1vez = [PATH_EXAMES, PATH_EM_CONSENTIMENTO]
        dados_finais["exames_solicitados"] = dados_finais.pop("exames_em_1vez")
        arquivos_preenchidos = preencher_formularios(
            arquivos_protocolo_1vez, dados_finais
        )
        return arquivos_preenchidos
    else:
        arquivos_protocolo_1vez = [PATH_EM_CONSENTIMENTO]
        arquivos_preenchidos = preencher_formularios(
            arquivos_protocolo_1vez, dados_finais
        )
        return arquivos_preenchidos


def glatiramer_renova(dados_finais):
    emitir_exames = dados_finais["exames"]
    if emitir_exames:
        dados_finais["exames_solicitados"] = dados_finais.pop("exames_em_renova")
        arquivos_protocolo_renovacao = [PATH_EXAMES]
        arquivos_preenchidos = preencher_formularios(
            arquivos_protocolo_renovacao, dados_finais
        )
        return arquivos_preenchidos

    else:
        return None
