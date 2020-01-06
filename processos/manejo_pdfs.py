import os
import random
from random import randint
import pypdftk
from django.conf import settings
from django.forms.models import model_to_dict
from datetime import datetime, timedelta
from pacientes.models import Paciente
from medicos.models import Medico
from processos.models import Processo

def preencher_formularios(lista_pdfs,dados_finais):
    '''Preenche os pdfs individualmente e gera os arquivos
    intermediários com nomes aleatórios '''
    arquivos = []
    cpf_paciente = dados_finais['cpf_paciente']
    for arquivo in lista_pdfs:
        aleatorio = random.randint(0,10000000000)
        arquivos.append(pypdftk.fill_form(arquivo,dados_finais,'{}_{}.pdf'.format(aleatorio,cpf_paciente)))
    return arquivos


def remover_pdfs_intermediarios(*arquivos):
    '''Remove os arquivos intermediários após a 
    concatenação '''
    for arquivo in arquivos:
        os.remove(arquivo)


def gerar_pdf_final(arquivos,path_pdf_final):
    ''' Concatena e achata os pdfs intermediários (preenchidos);
    gera o arquivo final para impressão'''
    pdf_final = pypdftk.concat(arquivos, path_pdf_final)
    return pdf_final


def selecionar_med_consentimento(medicamento_1,dados_finais):
    '''Responsável por definir o medicamento prescrito no
    check-list do termo de consentimento - isola o nome 
    do fármaco da dosagem '''
    med = medicamento_1.split((' '))
    nome_med = dados_finais['selecionar_med'] = med[0]
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

def gerar_dados_renovacao(primeira_data, processo_id):
    processo = Processo.objects.get(id=processo_id)
    dados_processo = model_to_dict(processo)
    dados_paciente = model_to_dict(processo.paciente)
    dados_medico = model_to_dict(processo.medico)
    dados_clinica = model_to_dict(processo.clinica)
    # pdftk falha se input não for string!
    dados_clinica['medicos'] = ''
    dados_clinica['usuarios'] = ''
    
    dados = {}
    dados.update(dados_medico)
    dados.update(dados_paciente)
    dados.update(dados_processo)
    dados.update(dados_clinica)
    dados['data_1'] = datetime.strptime(primeira_data, '%Y-%m-%d')
    return dados

       


class GeradorPDF():

    def __init__(self,dados_lme_base,dados_condicionais, path_lme_base):
        self.dados_lme_base = dados_lme_base
        self.dados_condicionais = dados_condicionais
        self.path_lme_base = path_lme_base

    
    def generico(self,dados_lme_base,path_lme_base):
        cpf_paciente = dados_lme_base['cpf_paciente']
        cid = dados_lme_base['cid']
        nome_final_pdf = f'tmp/pdf_final_{cpf_paciente}_{cid}.pdf'

        data1 = dados_lme_base['data_1']
        datas = formatacao_data(data1)

        dados_lme_base['data_1'] = datas[0]
        dados_lme_base['data_2'] = datas[1]
        dados_lme_base['data_3'] = datas[2]
        



        #Esse é o endereço de output lido pelo PDFTK "localmente"
        output_pdf_final = os.path.join('processos/static', nome_final_pdf)

        #Não me parece a melhor maneira de fazer isso. Essa é a URL para o redirect.
        path_pdf_final = settings.STATIC_URL + nome_final_pdf
        
        pdf = pypdftk.fill_form(path_lme_base,dados_lme_base,output_pdf_final)
        return pdf, path_pdf_final

    
    def emitir_exames(self,dados_lme_base):
        #Redundância
        if dados_lme_base['emitir_exames'] == 'sim':
            return True
        return False




