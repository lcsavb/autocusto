import os

import pypdftk

from paths import PATH_LME_BASE, PATH_EXAMES, PATH_DOR_CONSENTIMENTO, PATH_DOR_ESCALA
from dados import PATH_PDF_FINAL, dados_dor
from manejo_pdfs import GeradorPDF, remover_pdfs_intermediarios, preencher_formularios, gerar_pdf_final, selecionar_med_consentimento, adicionar_exames

path_lme_base = PATH_LME_BASE

class Dor(GeradorPDF):
    def __init__(self, dados_lme_base,dados_condicionais,path_lme_base):
        GeradorPDF.__init__(self,dados_lme_base,dados_condicionais,path_lme_base)
        self.dados_condicionais = dados_condicionais

                 
    def renovar(self,dados_lme_base,dados_condicionais,path_lme_base):
        dados_lme_base.update(dados_condicionais)
        dados_finais = dados_lme_base
        arquivos_base = [path_lme_base]
        emitir_exames = dados_finais['exames']

        arquivos_base = [path_lme_base, PATH_DOR_ESCALA]
        
        if emitir_exames:
            arquivos = adicionar_exames(arquivos_base,dados_finais)
        else:
            arquivos = preencher_formularios(arquivos_base, dados_finais)

        
        pdf = gerar_pdf_final(arquivos,PATH_PDF_FINAL)          


        remover_pdfs_intermediarios(*arquivos)
        return pdf


    def primeira_vez(self,dados_lme_base,dados_condicionais,path_lme_base):
        dados_lme_base.update(dados_condicionais)
        dados_finais = dados_lme_base
        medicamento = dados_finais['med1'].lower()
        emitir_exames = dados_finais['exames']
        
        arquivos_base = [path_lme_base, PATH_DOR_CONSENTIMENTO, PATH_DOR_ESCALA]

        selecionar_med_consentimento(medicamento,dados_finais)

        if emitir_exames:
            arquivos = adicionar_exames(arquivos_base,dados_finais)
        else:
            arquivos = preencher_formularios(arquivos_base, dados_finais)

        pdf = gerar_pdf_final(arquivos,PATH_PDF_FINAL)
        
        remover_pdfs_intermediarios(*arquivos)
        return pdf
