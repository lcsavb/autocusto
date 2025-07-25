

from paths import (
    PATH_LME_BASE,
    PATH_RELATORIO_AR,
    PATH_AR_CONSENTIMENTO,
)
from dados import PATH_PDF_FINAL, med_ar_grupo_1, meds_relatorio_ar
from manejo_pdfs import (
    GeradorPDF,
    remover_pdfs_intermediarios,
    preencher_formularios,
    gerar_pdf_final,
    selecionar_med_consentimento,
    adicionar_exames,
)

path_lme_base = PATH_LME_BASE


# rheumatoid arthritis
class Artrite_Reumatoide(GeradorPDF):
    def __init__(self, dados_lme_base, dados_condicionais, path_lme_base):
        GeradorPDF.__init__(self, dados_lme_base, dados_condicionais, path_lme_base)
        self.dados_condicionais = dados_condicionais

    # renew
    def renovar(self, dados_lme_base, dados_condicionais, path_lme_base):
        dados_lme_base.update(dados_condicionais)
        dados_finais = dados_lme_base
        arquivos_base = [path_lme_base]
        emitir_exames = dados_finais["exames"]

        arquivos_base = [path_lme_base]

        if emitir_exames:
            arquivos = adicionar_exames(arquivos_base, dados_finais)
        else:
            arquivos = preencher_formularios(arquivos_base, dados_finais)

        pdf = gerar_pdf_final(arquivos, PATH_PDF_FINAL)

        remover_pdfs_intermediarios(*arquivos)
        return pdf

    # first time
    def primeira_vez(self, dados_lme_base, dados_condicionais, path_lme_base):
        dados_lme_base.update(dados_condicionais)
        dados_finais = dados_lme_base
        medicamento = dados_finais["med1"].lower()
        emitir_exames = dados_finais["exames"]

        arquivos_base = [path_lme_base, PATH_AR_CONSENTIMENTO]

        medicamento = selecionar_med_consentimento(medicamento, dados_finais)

        if medicamento in meds_relatorio_ar:
            arquivos_base = [path_lme_base, PATH_AR_CONSENTIMENTO, PATH_RELATORIO_AR]

        if emitir_exames:

            if medicamento in med_ar_grupo_1:
                dados_finais["exames_solicitados"] = dados_finais.pop(
                    "exames_ar_grupo_1"
                )
                arquivos = adicionar_exames(arquivos_base, dados_finais)
            else:
                dados_finais["exames_solicitados"] = dados_finais.pop(
                    "exames_ar_grupo_2"
                )
                arquivos = adicionar_exames(arquivos_base, dados_finais)
        else:
            arquivos = preencher_formularios(arquivos_base, dados_finais)

        pdf = gerar_pdf_final(arquivos, PATH_PDF_FINAL)

        remover_pdfs_intermediarios(*arquivos)
        return pdf
