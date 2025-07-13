

from paths import PATH_LME_BASE, PATH_DISLIPIDEMIA_CONSENTIMENTO
from dados import PATH_PDF_FINAL
from manejo_pdfs import (
    GeradorPDF,
    remover_pdfs_intermediarios,
    preencher_formularios,
    gerar_pdf_final,
    selecionar_med_consentimento,
    adicionar_exames,
)

path_lme_base = PATH_LME_BASE


class Dislipidemia(GeradorPDF):
    def __init__(self, dados_lme_base, dados_condicionais, path_lme_base):
        GeradorPDF.__init__(self, dados_lme_base, dados_condicionais, path_lme_base)
        self.dados_condicionais = dados_condicionais

    def renovar(self, dados_lme_base, dados_condicionais, path_lme_base):
        dados_lme_base.update(dados_condicionais)
        dados_finais = dados_lme_base
        emitir_exames = dados_finais["exames"]
        idade = dados_finais["idade"]
        sexo = dados_finais["sexo"].lower()
        medicamento = dados_finais["med1"].lower()

        arquivos_base = [path_lme_base]

        medicamento = selecionar_med_consentimento(medicamento, dados_finais)

        if emitir_exames:
            dados_finais["exames_solicitados"] = dados_finais.pop(
                "dislipidemia_1vez_exames"
            )
            if sexo == "feminino" and int(idade) < 45:
                dados_finais["exames_solicitados"].append("Beta-HCG")
                if medicamento == "ácido":
                    protocolo_acido_nicotinico(dados_finais)
                    arquivos = adicionar_exames(arquivos_base, dados_finais)
                else:
                    arquivos = adicionar_exames(arquivos_base, dados_finais)
            else:
                if medicamento == "ácido":
                    protocolo_acido_nicotinico(dados_finais)
                    arquivos = adicionar_exames(arquivos_base, dados_finais)
                else:
                    arquivos = adicionar_exames(arquivos_base, dados_finais)
        else:
            if medicamento == "ácido":
                protocolo_acido_nicotinico(dados_finais)
                arquivos = preencher_formularios(arquivos_base, dados_finais)
            else:
                arquivos = preencher_formularios(arquivos_base, dados_finais)

        pdf_dlp = gerar_pdf_final(arquivos, PATH_PDF_FINAL)
        remover_pdfs_intermediarios(*arquivos)
        return pdf_dlp

    def primeira_vez(self, dados_lme_base, dados_condicionais, path_lme_base):
        dados_lme_base.update(dados_condicionais)
        dados_finais = dados_lme_base
        emitir_exames = dados_finais["exames"]
        idade = dados_finais["idade"]
        sexo = dados_finais["sexo"].lower()
        medicamento = dados_finais["med1"].lower()

        arquivos_base = [path_lme_base, PATH_DISLIPIDEMIA_CONSENTIMENTO]

        medicamento = selecionar_med_consentimento(medicamento, dados_finais)
        print(medicamento)

        if emitir_exames:
            dados_finais["exames_solicitados"] = dados_finais.pop(
                "dislipidemia_1vez_exames"
            )
            if sexo == "feminino" and int(idade) < 45:
                dados_finais["exames_solicitados"].append("Beta-HCG")
                if medicamento == "ácido":
                    protocolo_acido_nicotinico(dados_finais)
                    arquivos = adicionar_exames(arquivos_base, dados_finais)
                else:
                    arquivos = adicionar_exames(arquivos_base, dados_finais)
            else:
                if medicamento == "ácido":
                    protocolo_acido_nicotinico(dados_finais)
                    arquivos = adicionar_exames(arquivos_base, dados_finais)
                else:
                    arquivos = adicionar_exames(arquivos_base, dados_finais)
        else:
            if medicamento == "ácido":
                protocolo_acido_nicotinico(dados_finais)
                arquivos = preencher_formularios(arquivos_base, dados_finais)
            else:
                arquivos = preencher_formularios(arquivos_base, dados_finais)

        pdf_dlp = gerar_pdf_final(arquivos, PATH_PDF_FINAL)
        remover_pdfs_intermediarios(*arquivos)
        return pdf_dlp


def protocolo_acido_nicotinico(dados_finais):
    dados_finais["trat_previo"] = "sim"
    dados_finais["tratamentos_previos"] = dados_finais.pop("ac_nicotinico_trat_previo")
    return dados_finais
