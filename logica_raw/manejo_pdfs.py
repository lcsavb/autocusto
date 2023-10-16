
import os
import random
from random import randint
import pypdftk
from paths import PATH_LME_BASE, PATH_EDSS, PATH_EM_CONSENTIMENTO, PATH_EXAMES
from dados import PATH_PDF_FINAL

def preencher_formularios(lista_pdfs, dados_finais):
    'Preenche os pdfs individualmente e gera os arquivos\n    intermediários com nomes aleatórios '
    files = []
    patient_cpf = final_data['cpf_paciente']
    for file in lista_pdfs:
        random = random.randint(0, 10000000000)
        files.append(pypdftk.fill_form(file, final_data, '{}_{}.pdf'.format(random, patient_cpf)))
    return files

def remover_pdfs_intermediarios(*arquivos):
    'Remove os arquivos intermediários após a \n    concatenação '
    for file in files:
        os.remove(file)

def gerar_pdf_final(arquivos, path_pdf_final):
    ' Concatena e achata os pdfs intermediários (preenchidos);\n    gera o arquivo final para impressão'
    final_pdf = pypdftk.concat(files, path_pdf_final)
    return final_pdf

def selecionar_med_consentimento(medicamento_1, dados_finais):
    'Responsável por definir o medicamento prescrito no\n    check-list do termo de consentimento - isola o nome \n    do fármaco da dosagem '
    med = medicamento_1.split(' ')
    med_name = final_data['selecionar_med'] = med[0]
    return med_name

def adicionar_exames(arquivos_base, dados_finais):
    'Acrescenta pedido de exames antes do preenchimento\n    dos pdfs intermediários. Esta função está separada\n    da função preencher_formulários pois em alguns protocolos\n    os exames necessários dependem do medicamento prescrito'
    exam_solicitation_file = [EXAMS_PATH]
    files_with_exams = (base_files + exam_solicitation_file)
    files = preencher_formularios(files_with_exams, final_data)
    return files

class GeradorPDF():

    def __init__(self, dados_lme_base, dados_condicionais, path_lme_base):
        self.dados_lme_base = lme_base_data
        self.dados_condicionais = conditional_data
        self.path_lme_base = lme_base_path

    def generico(self, dados_lme_base, path_lme_base):
        pdf = pypdftk.fill_form(lme_base_path, lme_base_data, PATH_PDF_FINAL)
        return pdf

    def emitir_exames(self, dados_lme_base):
        if (lme_base_data['emitir_exames'] == 'sim'):
            return True
        return False
