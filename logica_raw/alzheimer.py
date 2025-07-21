

from paths import PATH_LME_BASE, PATH_EXAMES, PATH_DA_CONSENTIMENTO, PATH_CDR, PATH_MEEM
from dados import PATH_PDF_FINAL
from manejo_pdfs import (
    GeradorPDF,
    remover_pdfs_intermediarios,
    preencher_formularios,
    gerar_pdf_final,
    selecionar_med_consentimento,
)

path_lme_base = PATH_LME_BASE


class Alzheimer(GeradorPDF):
    def __init__(self, dados_lme_base, dados_condicionais, path_lme_base):
        GeradorPDF.__init__(self, dados_lme_base, dados_condicionais, path_lme_base)
        self.dados_condicionais = dados_condicionais

    # renew
    def renovar(self, dados_lme_base, dados_condicionais, path_lme_base):
        dados_lme_base.update(dados_condicionais)
        dados_finais = dados_lme_base
        arquivos_base = [path_lme_base, PATH_CDR, PATH_MEEM]

        arquivos = preencher_formularios(arquivos_base, dados_finais)
        pdf_da = gerar_pdf_final(arquivos, PATH_PDF_FINAL)

        remover_pdfs_intermediarios(*arquivos)
        return pdf_da

    # first time
    def primeira_vez(self, dados_lme_base, dados_condicionais, path_lme_base):
        dados_lme_base.update(dados_condicionais)
        dados_finais = dados_lme_base
        emitir_exames = dados_finais["exames"]
        medicamento = dados_finais["med1"].lower()

        arquivos_base = [path_lme_base, PATH_CDR, PATH_MEEM, PATH_DA_CONSENTIMENTO]

        selecionar_med_consentimento(medicamento, dados_finais)

        if emitir_exames:
            dados_finais["exames_solicitados"] = dados_finais.pop("exames_da_1vez")
            arquivo_exame = [PATH_EXAMES]
            arquivos_com_exames = arquivos_base + arquivo_exame
            arquivos = preencher_formularios(arquivos_com_exames, dados_finais)
        else:
            arquivos = preencher_formularios(arquivos_base, dados_finais)

        pdf_da = gerar_pdf_final(arquivos, PATH_PDF_FINAL)

        remover_pdfs_intermediarios(*arquivos)
        return pdf_da
