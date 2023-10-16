
import os
import pypdftk
from paths import PATH_LME_BASE, PATH_EDSS, PATH_EM_CONSENTIMENTO, PATH_EXAMES, PATH_FINGO_MONIT, PATH_RELATORIO, PATH_NATA_EXAMES
from dados import PATH_PDF_FINAL
from manejo_pdfs import GeradorPDF, remover_pdfs_intermediarios, preencher_formularios, gerar_pdf_final

class EscleroseMultipla(GeradorPDF):

    def __init__(self, dados_lme_base, dados_condicionais, path_lme_base):
        GeradorPDF.__init__(self, lme_base_data, conditional_data, lme_base_path)
        self.dados_condicionais = conditional_data

    def renovar(self, dados_lme_base, dados_condicionais, path_lme_base):
        lme_base_data.update(conditional_data)
        final_data = lme_base_data
        medication = final_data['med1'].lower()
        template_files = [lme_base_path, PATH_EDSS]
        base_files = preencher_formularios(template_files, final_data)
        if ('fingolimode' in medication):
            conditional_files = fingolimode_renova(final_data)
            files = (base_files + conditional_files)
        elif ('betainterferon' in medication):
            conditional_files = betainterferon_renova(final_data)
            files = (base_files + conditional_files)
        elif ('natalizumabe' in medication):
            conditional_files = natalizumabe_renova(final_data)
            files = (base_files + conditional_files)
        elif ('fumarato' in medication):
            conditional_files = fumarato_renova(final_data)
            files = (base_files + conditional_files)
        elif ('glatiramer' in medication):
            conditional_files = glatiramer_renova(final_data)
            files = (base_files + conditional_files)
        elif ('teriflunomida' in medication):
            conditional_files = teriflunomida_renova(final_data)
            files = (base_files + conditional_files)
        elif ('azatioprina' in medication):
            conditional_files = azatioprina_renova(final_data)
            files = (base_files + conditional_files)
        multiple_sclerosis_pdf = gerar_pdf_final(files, PATH_PDF_FINAL)
        remover_pdfs_intermediarios(*files)
        return multiple_sclerosis_pdf

    def primeira_vez(self, dados_lme_base, dados_condicionais, path_lme_base):
        lme_base_data.update(conditional_data)
        final_data = lme_base_data
        medication = final_data['med1'].lower()
        issue_exams = final_data['exames']
        template_files = [lme_base_path, PATH_EDSS]
        base_files = preencher_formularios(template_files, final_data)
        if ('fingolimode' in medication):
            conditional_files = fingolimode_1vez(final_data)
            files = (base_files + conditional_files)
        elif (('betainterferon' in medication) and issue_exams):
            conditional_files = betainterferon_1vez(final_data)
            files = (base_files + conditional_files)
        elif ('natalizumabe' in medication):
            conditional_files = natalizumabe_1vez(final_data)
            files = (base_files + conditional_files)
        elif ('fumarato' in medication):
            conditional_files = fumarato_1vez(final_data)
            files = (base_files + conditional_files)
        elif ('glatiramer' in medication):
            conditional_files = glatiramer_1vez(final_data)
            files = (base_files + conditional_files)
        elif ('teriflunomida' in medication):
            conditional_files = teriflunomida_1vez(final_data)
            files = (base_files + conditional_files)
        elif ('azatioprina' in medication):
            conditional_files = azatioprina_1vez(final_data)
            files = (base_files + conditional_files)
        multiple_sclerosis_pdf = gerar_pdf_final(files, PATH_PDF_FINAL)
        remover_pdfs_intermediarios(*files)
        print(multiple_sclerosis_pdf)
        return multiple_sclerosis_pdf

def fingolimode_1vez(dados_finais):
    issue_exams = final_data['exames']
    final_data['relatorio'] = final_data.pop('relatorio_fingolimode_1vez')
    if issue_exams:
        final_data['exames_solicitados'] = final_data.pop('exames_em_1vez')
        first_time_protocol_files = [FINGOLIMOD_MONITORING_PATH, EXAMS_PATH]
        filled_files = preencher_formularios(first_time_protocol_files, final_data)
        return filled_files
    else:
        first_time_protocol_files = [FINGOLIMOD_MONITORING_PATH]
        filled_files = preencher_formularios(first_time_protocol_files, final_data)
        return filled_files

def fingolimode_renova(dados_finais):
    issue_exams = final_data['exames']
    if issue_exams:
        final_data['exames_solicitados'] = final_data.pop('exames_em_renova')
        arquivos_protocolo_renovacao = [EXAMS_PATH]
        filled_files = preencher_formularios(arquivos_protocolo_renovacao, final_data)
        return filled_files
    else:
        return None

def natalizumabe_1vez(dados_finais):
    issue_exams = final_data['exames']
    final_data['relatorio'] = final_data.pop('relatorio_natalizumabe_1vez')
    final_data['consentimento_medicamento'] = 'natalizumabe'
    if issue_exams:
        first_time_protocol_files = [PATH_REPORT, EXAMS_PATH, EM_CONSENT_PATH]
        final_data['exames_solicitados'] = final_data.pop('exames_em_1vez')
        filled_files = preencher_formularios(first_time_protocol_files, final_data)
        return filled_files
    else:
        first_time_protocol_files = [PATH_REPORT, EM_CONSENT_PATH]
        filled_files = preencher_formularios(first_time_protocol_files, final_data)
        return filled_files

def natalizumabe_renova(dados_finais):
    issue_exams = final_data['exames']
    if issue_exams:
        final_data['exames_solicitados'] = final_data.pop('exames_nata_renova')
        arquivos_protocolo_renovacao = [NATA_EXAMS_PATH]
        filled_files = preencher_formularios(arquivos_protocolo_renovacao, final_data)
        return filled_files
    else:
        return None

def betainterferon_1vez(dados_finais):
    issue_exams = final_data['exames']
    final_data['consentimento_medicamento'] = 'betainterferona1a'
    if issue_exams:
        first_time_protocol_files = [EXAMS_PATH, EM_CONSENT_PATH]
        final_data['exames_solicitados'] = final_data.pop('exames_em_1vez')
        filled_files = preencher_formularios(first_time_protocol_files, final_data)
        return filled_files
    else:
        first_time_protocol_files = [EM_CONSENT_PATH]
        filled_files = preencher_formularios(first_time_protocol_files, final_data)
        return filled_files

def betainterferon_renova(dados_finais):
    issue_exams = final_data['exames']
    if issue_exams:
        final_data['exames_solicitados'] = final_data.pop('exames_em_renova')
        arquivos_protocolo_renovacao = [EXAMS_PATH]
        filled_files = preencher_formularios(arquivos_protocolo_renovacao, final_data)
        return filled_files
    else:
        return None

def fumarato_1vez(dados_finais):
    issue_exams = final_data['exames']
    final_data['relatorio'] = final_data.pop('relatorio_fumarato_1vez')
    final_data['consentimento_medicamento'] = 'dimetila'
    if issue_exams:
        final_data['exames_solicitados'] = final_data.pop('exames_em_1vez')
        first_time_protocol_files = [EXAMS_PATH, EM_CONSENT_PATH, PATH_REPORT]
        filled_files = preencher_formularios(first_time_protocol_files, final_data)
        return filled_files
    else:
        first_time_protocol_files = [EM_CONSENT_PATH, PATH_REPORT]
        filled_files = preencher_formularios(first_time_protocol_files, final_data)
        return filled_files

def fumarato_renova(dados_finais):
    issue_exams = final_data['exames']
    if issue_exams:
        final_data['exames_solicitados'] = final_data.pop('exames_em_renova')
        arquivos_protocolo_renovacao = [EXAMS_PATH]
        filled_files = preencher_formularios(arquivos_protocolo_renovacao, final_data)
        return filled_files
    else:
        return None

def azatioprina_1vez(dados_finais):
    issue_exams = final_data['exames']
    final_data['consentimento_medicamento'] = 'azatioprina'
    if issue_exams:
        first_time_protocol_files = [EXAMS_PATH, EM_CONSENT_PATH]
        final_data['exames_solicitados'] = final_data.pop('exames_em_1vez')
        filled_files = preencher_formularios(first_time_protocol_files, final_data)
        return filled_files
    else:
        first_time_protocol_files = [EM_CONSENT_PATH]
        filled_files = preencher_formularios(first_time_protocol_files, final_data)
        return filled_files

def azatioprina_renova(dados_finais):
    issue_exams = final_data['exames']
    if issue_exams:
        final_data['exames_solicitados'] = final_data.pop('exames_em_renova')
        arquivos_protocolo_renovacao = [EXAMS_PATH]
        filled_files = preencher_formularios(arquivos_protocolo_renovacao, final_data)
        return filled_files
    else:
        return None

def teriflunomida_1vez(dados_finais):
    issue_exams = final_data['exames']
    final_data['consentimento_medicamento'] = 'teriflunomida'
    if issue_exams:
        first_time_protocol_files = [EXAMS_PATH, EM_CONSENT_PATH]
        final_data['exames_solicitados'] = final_data.pop('exames_em_1vez')
        filled_files = preencher_formularios(first_time_protocol_files, final_data)
        return filled_files
    else:
        first_time_protocol_files = [EM_CONSENT_PATH]
        filled_files = preencher_formularios(first_time_protocol_files, final_data)
        return filled_files

def teriflunomida_renova(dados_finais):
    issue_exams = final_data['exames']
    if issue_exams:
        final_data['exames_solicitados'] = final_data.pop('exames_em_renova')
        arquivos_protocolo_renovacao = [EXAMS_PATH]
        filled_files = preencher_formularios(arquivos_protocolo_renovacao, final_data)
        return filled_files
    else:
        return None

def glatiramer_1vez(dados_finais):
    issue_exams = final_data['exames']
    final_data['consentimento_medicamento'] = 'glatiramer'
    if issue_exams:
        first_time_protocol_files = [EXAMS_PATH, EM_CONSENT_PATH]
        final_data['exames_solicitados'] = final_data.pop('exames_em_1vez')
        filled_files = preencher_formularios(first_time_protocol_files, final_data)
        return filled_files
    else:
        first_time_protocol_files = [EM_CONSENT_PATH]
        filled_files = preencher_formularios(first_time_protocol_files, final_data)
        return filled_files

def glatiramer_renova(dados_finais):
    issue_exams = final_data['exames']
    if issue_exams:
        final_data['exames_solicitados'] = final_data.pop('exames_em_renova')
        arquivos_protocolo_renovacao = [EXAMS_PATH]
        filled_files = preencher_formularios(arquivos_protocolo_renovacao, final_data)
        return filled_files
    else:
        return None
