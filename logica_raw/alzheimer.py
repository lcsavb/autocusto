
import os
import pypdftk
from paths import PATH_LME_BASE, PATH_EXAMES, PATH_DA_CONSENTIMENTO, PATH_CDR, PATH_MEEM
from dados import PATH_PDF_FINAL
from manejo_pdfs import GeradorPDF, remover_pdfs_intermediarios, preencher_formularios, gerar_pdf_final, selecionar_med_consentimento
lme_base_path = LME_BASE_PATH

class Alzheimer(GeradorPDF):

    def __init__(self, dados_lme_base, dados_condicionais, path_lme_base):
        GeradorPDF.__init__(self, lme_base_data, conditional_data, lme_base_path)
        self.dados_condicionais = conditional_data

    def renovar(self, dados_lme_base, dados_condicionais, path_lme_base):
        lme_base_data.update(conditional_data)
        final_data = lme_base_data
        base_files = [lme_base_path, CDR_PATH, MEEM_PATH]
        files = preencher_formularios(base_files, final_data)
        alzheimer_pdf = gerar_pdf_final(files, PATH_PDF_FINAL)
        remover_pdfs_intermediarios(*files)
        return alzheimer_pdf

    def primeira_vez(self, dados_lme_base, dados_condicionais, path_lme_base):
        lme_base_data.update(conditional_data)
        final_data = lme_base_data
        issue_exams = final_data['exames']
        medication = final_data['med1'].lower()
        base_files = [lme_base_path, CDR_PATH, MEEM_PATH, CONSENT_PATH]
        selecionar_med_consentimento(medication, final_data)
        if issue_exams:
            final_data['exames_solicitados'] = final_data.pop('exames_da_1vez')
            exam_solicitation_file = [EXAMS_PATH]
            files_with_exams = (base_files + exam_solicitation_file)
            files = preencher_formularios(files_with_exams, final_data)
        else:
            files = preencher_formularios(base_files, final_data)
        alzheimer_pdf = gerar_pdf_final(files, PATH_PDF_FINAL)
        remover_pdfs_intermediarios(*files)
        return alzheimer_pdf
