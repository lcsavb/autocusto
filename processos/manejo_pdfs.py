
import os
import random
import glob
from random import randint
import pypdftk
from django.conf import settings
from django.forms.models import model_to_dict
from datetime import datetime, timedelta
from pacientes.models import Paciente
from medicos.models import Medico
from processos.models import Processo, Protocolo, Medicamento

def preencher_formularios(lista_pdfs, dados_finais):
    'Preenche os pdfs individualmente e gera os arquivos\n    intermediários com nomes aleatórios '
    files = []
    for file in lista_pdfs:
        random = (str(random.randint(0, 10000000000)) + final_data['cns_medico'])
        output_pdf = os.path.join(settings.BASE_DIR, 'static/tmp', '{}.pdf'.format(random))
        files.append(pypdftk.fill_form(file, final_data, output_pdf))
    return files

def remover_pdfs_intermediarios(arquivos):
    'Remove os arquivos intermediários após a \n    concatenação '
    for file in files:
        os.remove(file)

def gerar_pdf_final(arquivos, path_pdf_final):
    ' Concatena e achata os pdfs intermediários (preenchidos);\n    gera o arquivo final para impressão'
    final_pdf = pypdftk.concat(files, path_pdf_final)
    return final_pdf

def adicionar_exames(arquivos_base, dados_finais):
    'Acrescenta pedido de exames antes do preenchimento\n    dos pdfs intermediários. Esta função está separada\n    da função preencher_formulários pois em alguns protocolos\n    os exames necessários dependem do medicamento prescrito'
    exam_solicitation_file = [EXAMS_PATH]
    files_with_exams = (base_files + exam_solicitation_file)
    files = preencher_formularios(files_with_exams, final_data)
    return files

def formatacao_data(dados):
    'Recebe a data inicial do processo, cria as datas\n     subsequentes e formata para o padrão brasileiro'
    month = 2
    dias = 30
    while (month <= 6):
        data[f'data_{month}'] = (data['data_1'] + timedelta(days=dias)).strftime('%d/%m/%Y')
        dias += 30
        month += 1
    data['data_1'] = data['data_1'].strftime('%d/%m/%Y')

def ajustar_campo_18(dados_lme):
    if (dados_lme['preenchido_por'] != 'medico'):
        del dados_lme['cpf_paciente']
        dados_lme['etnia'] = ''
        del dados_lme['telefone1_paciente']
        del dados_lme['telefone2_paciente']
        del dados_lme['email_paciente']
        dados_lme['escolha_documento'] = ''

class GeradorPDF():

    def __init__(self, dados_lme_base, path_lme_base):
        self.dados_lme_base = lme_base_data
        self.path_lme_base = lme_base_path

    def generico(self, dados_lme_base, path_lme_base):
        patient_cpf = lme_base_data['cpf_paciente']
        icd = lme_base_data['cid']
        final_name_pdf = f'pdf_final_{patient_cpf}_{icd}.pdf'
        first_time = lme_base_data['consentimento']
        report = lme_base_data['relatorio']
        exams = lme_base_data['exames']
        formatacao_data(lme_base_data)
        base_files = [lme_base_path]
        protocol = Protocolo.objects.get(doenca__cid=icd)
        try:
            conditional_pdfs_directory = os.path.join(settings.PATH_PDF_DIR, protocol.nome, 'pdfs_base/')
            conditional_base_pdfs = glob.glob((conditional_pdfs_directory + '*.*'))
            for pdf in conditional_base_pdfs:
                base_files.append(pdf)
        except:
            pass
        if (first_time == 'True'):
            try:
                id_med = lme_base_data['id_med1']
                consent_pdf = os.path.join(settings.PATH_PDF_DIR, protocol.nome, 'consentimento.pdf')
                lme_base_data['consentimento_medicamento'] = Medicamento.objects.get(id=id_med).nome
                base_files.append(consent_pdf)
            except:
                pass
        if report:
            base_files.append(settings.PATH_RELATORIO)
        if exams:
            base_files.append(settings.PATH_EXAMES)
        ajustar_campo_18(lme_base_data)
        path_pdf_final = os.path.join(settings.STATIC_URL, 'tmp', final_name_pdf)
        final_output_pdf = os.path.join(settings.BASE_DIR, 'static/tmp', final_name_pdf)
        intermediary_filled_pdfs = preencher_formularios(base_files, lme_base_data)
        pdf = gerar_pdf_final(intermediary_filled_pdfs, final_output_pdf)
        remover_pdfs_intermediarios(intermediary_filled_pdfs)
        return (pdf, path_pdf_final)
