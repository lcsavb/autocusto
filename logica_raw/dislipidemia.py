
import os
import pypdftk
from paths import PATH_LME_BASE, PATH_EXAMES, PATH_DISLIPIDEMIA_CONSENTIMENTO
from dados import PATH_PDF_FINAL, dislipidemia_1vez_exames, fibratos_1vez_exames
from manejo_pdfs import GeradorPDF, remover_pdfs_intermediarios, preencher_formularios, gerar_pdf_final, selecionar_med_consentimento, adicionar_exames
lme_base_path = LME_BASE_PATH

class Dislipidemia(GeradorPDF):

    def __init__(self, dados_lme_base, dados_condicionais, path_lme_base):
        GeradorPDF.__init__(self, lme_base_data, conditional_data, lme_base_path)
        self.dados_condicionais = conditional_data

    def renovar(self, dados_lme_base, dados_condicionais, path_lme_base):
        lme_base_data.update(conditional_data)
        final_data = lme_base_data
        issue_exams = final_data['exames']
        age = final_data['idade']
        gender = final_data['sexo'].lower()
        medication = final_data['med1'].lower()
        base_files = [lme_base_path]
        medication = selecionar_med_consentimento(medication, final_data)
        if issue_exams:
            final_data['exames_solicitados'] = final_data.pop('dislipidemia_1vez_exames')
            if ((gender == 'feminino') and (int(age) < 45)):
                final_data['exames_solicitados'].append('Beta-HCG')
                if (medication == 'ácido'):
                    protocolo_acido_nicotinico(final_data)
                    files = adicionar_exames(base_files, final_data)
                else:
                    files = adicionar_exames(base_files, final_data)
            elif (medication == 'ácido'):
                protocolo_acido_nicotinico(final_data)
                files = adicionar_exames(base_files, final_data)
            else:
                files = adicionar_exames(base_files, final_data)
        elif (medication == 'ácido'):
            protocolo_acido_nicotinico(final_data)
            files = preencher_formularios(base_files, final_data)
        else:
            files = preencher_formularios(base_files, final_data)
        pdf_dlp = gerar_pdf_final(files, PATH_PDF_FINAL)
        remover_pdfs_intermediarios(*files)
        return pdf_dlp

    def primeira_vez(self, dados_lme_base, dados_condicionais, path_lme_base):
        lme_base_data.update(conditional_data)
        final_data = lme_base_data
        issue_exams = final_data['exames']
        age = final_data['idade']
        gender = final_data['sexo'].lower()
        medication = final_data['med1'].lower()
        base_files = [lme_base_path, DISLIPIDEMIA_CONSENT_PATH]
        medication = selecionar_med_consentimento(medication, final_data)
        print(medication)
        if issue_exams:
            final_data['exames_solicitados'] = final_data.pop('dislipidemia_1vez_exames')
            if ((gender == 'feminino') and (int(age) < 45)):
                final_data['exames_solicitados'].append('Beta-HCG')
                if (medication == 'ácido'):
                    protocolo_acido_nicotinico(final_data)
                    files = adicionar_exames(base_files, final_data)
                else:
                    files = adicionar_exames(base_files, final_data)
            elif (medication == 'ácido'):
                protocolo_acido_nicotinico(final_data)
                files = adicionar_exames(base_files, final_data)
            else:
                files = adicionar_exames(base_files, final_data)
        elif (medication == 'ácido'):
            protocolo_acido_nicotinico(final_data)
            files = preencher_formularios(base_files, final_data)
        else:
            files = preencher_formularios(base_files, final_data)
        pdf_dlp = gerar_pdf_final(files, PATH_PDF_FINAL)
        remover_pdfs_intermediarios(*files)
        return pdf_dlp

def protocolo_acido_nicotinico(dados_finais):
    final_data['trat_previo'] = 'sim'
    final_data['tratamentos_previos'] = final_data.pop('ac_nicotinico_trat_previo')
    return final_data
