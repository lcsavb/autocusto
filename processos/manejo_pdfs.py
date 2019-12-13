import os
import random
from random import randint
import pypdftk
from django.conf import settings


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
       


class GeradorPDF():

    def __init__(self,dados_lme_base,dados_condicionais, path_lme_base):
        self.dados_lme_base = dados_lme_base
        self.dados_condicionais = dados_condicionais
        self.path_lme_base = path_lme_base

    
    def generico(self,dados_lme_base,path_lme_base):
        cpf_paciente = dados_lme_base['cpf_paciente']
        cid = dados_lme_base['cid']
        nome_final_pdf = f'tmp/pdf_final_{cpf_paciente}_{cid}.pdf'
        path_pdf_final = os.path.join(settings.BASE_DIR, 'processos/static', nome_final_pdf)
        
        
        pdf = pypdftk.fill_form(path_lme_base,dados_lme_base,path_pdf_final)
        return pdf, path_pdf_final

    
    def emitir_exames(self,dados_lme_base):
        if dados_lme_base['emitir_exames'] == 'sim':
            return True
        return False




