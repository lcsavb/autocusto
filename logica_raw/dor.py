
import os
import pypdftk
from paths import PATH_LME_BASE, PATH_EXAMES, PATH_DOR_CONSENTIMENTO, PATH_DOR_ESCALA
from dados import PATH_PDF_FINAL, dados_dor
from manejo_pdfs import GeradorPDF, remover_pdfs_intermediarios, preencher_formularios, gerar_pdf_final, selecionar_med_consentimento, adicionar_exames
lme_base_path = LME_BASE_PATH

class Dor(GeradorPDF):

    def __init__(self, dados_lme_base, dados_condicionais, path_lme_base):
        GeradorPDF.__init__(self, lme_base_data, conditional_data, lme_base_path)
        self.dados_condicionais = conditional_data

    def renovar(self, dados_lme_base, dados_condicionais, path_lme_base):
        lme_base_data.update(conditional_data)
        final_data = lme_base_data
        base_files = [lme_base_path]
        issue_exams = final_data['exames']
        base_files = [lme_base_path, PAIN_SCALE_PATH]
        if issue_exams:
            files = adicionar_exames(base_files, final_data)
        else:
            files = preencher_formularios(base_files, final_data)
        pdf = gerar_pdf_final(files, PATH_PDF_FINAL)
        remover_pdfs_intermediarios(*files)
        return pdf

    def primeira_vez(self, dados_lme_base, dados_condicionais, path_lme_base):
        lme_base_data.update(conditional_data)
        final_data = lme_base_data
        medication = final_data['med1'].lower()
        issue_exams = final_data['exames']
        base_files = [lme_base_path, PATH_DOR_CONSENTIMENTO, PAIN_SCALE_PATH]
        selecionar_med_consentimento(medication, final_data)
        if issue_exams:
            files = adicionar_exames(base_files, final_data)
        else:
            files = preencher_formularios(base_files, final_data)
        pdf = gerar_pdf_final(files, PATH_PDF_FINAL)
        remover_pdfs_intermediarios(*files)
        return pdf
