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
from processos.models import Processo, Protocolo


def preencher_formularios(lista_pdfs,dados_finais):
    '''Preenche os pdfs individualmente e gera os arquivos
    intermediários com nomes aleatórios '''
    arquivos = []
    for arquivo in lista_pdfs:
        aleatorio = random.randint(0,10000000000)
        output_pdf = os.path.join(settings.BASE_DIR, 'static/tmp', '{}.pdf'.format(aleatorio))
        arquivos.append(pypdftk.fill_form(arquivo,dados_finais,output_pdf))
    return arquivos


def remover_pdfs_intermediarios(arquivos):
    '''Remove os arquivos intermediários após a 
    concatenação '''
    for arquivo in arquivos:
        os.remove(arquivo)


def gerar_pdf_final(arquivos,path_pdf_final):
    ''' Concatena e achata os pdfs intermediários (preenchidos);
    gera o arquivo final para impressão'''
    pdf_final = pypdftk.concat(arquivos, path_pdf_final)
    return pdf_final


def selecionar_med_consentimento(medicamento_1):
    '''Responsável por definir o medicamento prescrito no
    check-list do termo de consentimento - isola o nome 
    do fármaco da dosagem '''
    med = medicamento_1.split((' '))
    nome_med = med[0]
    return nome_med


def adicionar_exames(arquivos_base,dados_finais):
    '''Acrescenta pedido de exames antes do preenchimento
    dos pdfs intermediários. Esta função está separada
    da função preencher_formulários pois em alguns protocolos
    os exames necessários dependem do medicamento prescrito'''
    arquivo_exame = [PATH_EXAMES]
    arquivos_com_exames = arquivos_base + arquivo_exame
    arquivos = preencher_formularios(arquivos_com_exames,dados_finais)
    return arquivos


def formatacao_data(data):
    '''Recebe a data inicial do processo, cria as datas
     subsequentes e formata para o padrão brasileiro'''
    data2 = (data + timedelta(days=30)).strftime('%d/%m/%Y')
    data3 = (data + timedelta(days=60)).strftime('%d/%m/%Y')
    data1 = data.strftime('%d/%m/%Y')
    datas = [data1, data2, data3]
    return datas

    # dados = {}
    # dados.update(dados_medico)
    # dados.update(dados_paciente)
    # dados.update(dados_processo)
    # dados.update(dados_clinica)
    # dados['data_1'] = datetime.strptime(primeira_data, '%Y-%m-%d')
    # return dados


def ajustar_campo_18(dados_lme):
    if dados_lme['preenchido_por'] != 'medico':
        del dados_lme['cpf_paciente']
        del dados_lme['etnia']
        del dados_lme['telefone1_paciente']
        del dados_lme['telefone2_paciente']
        del dados_lme['email_paciente']
        dados_lme['escolha_documento'] = ''
    else:
        pass


class GeradorPDF():

    def __init__(self,dados_lme_base,dados_condicionais, path_lme_base):
        self.dados_lme_base = dados_lme_base
        self.dados_condicionais = dados_condicionais
        self.path_lme_base = path_lme_base

    
    def generico(self,dados_lme_base,path_lme_base):
        cpf_paciente = dados_lme_base['cpf_paciente']
        cid = dados_lme_base['cid']
        nome_final_pdf = f'pdf_final_{cpf_paciente}_{cid}.pdf'
        primeira_vez = dados_lme_base['consentimento']

        data1 = dados_lme_base['data_1']
        datas = formatacao_data(data1)

        dados_lme_base['data_1'] = datas[0]
        dados_lme_base['data_2'] = datas[1]
        dados_lme_base['data_3'] = datas[2]

        arquivos_base = [path_lme_base]
        protocolo = Protocolo.objects.get(doenca__cid=cid)

        try:
            dir_pdfs_condicionais = os.path.join(settings.PATH_PDF_DIR, protocolo.nome, 'pdfs_base/')
            pdfs_condicionais_base = glob.glob(dir_pdfs_condicionais + '*.*')
            for pdf in pdfs_condicionais_base:
                arquivos_base.append(pdf)
        except:
            pass

        if primeira_vez == 'True':
            try:
                consentimento_pdf = os.path.join(settings.PATH_PDF_DIR, protocolo.nome, 'consentimento.pdf')
                dados_lme_base['consentimento_medicamento'] = selecionar_med_consentimento(dados_lme_base['med1'])
                arquivos_base.append(consentimento_pdf)
                print(consentimento_pdf, 'ENTROU')
            except:
                pass

        ## Remove o cpf do campo 18 se preenchimento não foi pelo médico
        ajustar_campo_18(dados_lme_base)

        path_pdf_final = os.path.join(settings.STATIC_URL, 'tmp', nome_final_pdf)
        output_pdf_final = os.path.join(settings.BASE_DIR, 'static/tmp', nome_final_pdf)
        pdfs_intermediarios_preenchidos = preencher_formularios(arquivos_base,dados_lme_base)
        pdf = gerar_pdf_final(pdfs_intermediarios_preenchidos,output_pdf_final)
        remover_pdfs_intermediarios(pdfs_intermediarios_preenchidos)

        return pdf, path_pdf_final

    
    def emitir_exames(self,dados_lme_base):
        #Redundância
        if dados_lme_base['emitir_exames'] == 'sim':
            return True
        return False




